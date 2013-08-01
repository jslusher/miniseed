# -*- coding: utf-8 -*-
from __future__ import unicode_literals


from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
from libcloud.compute.deployment import FileDeployment, \
    MultiStepDeployment, ScriptDeployment
from libcloud.compute.ssh import SSHClient

from seed import settings
from seed.exceptions import SeedZeroNameError, SeedAMIDoesNotExistError, \
    SeedMachineDoesNotExistError, SeedDuplicateNameError

from seed.utils.drivers.aws import locate_security_group, \
    obtain_size, import_keypair, get_availability_zone
from seed.utils.api import obtain_driver, find_script
from seed.utils.drivers.aws import locate_security_group
from seed.utils.keys import get_public_key_from_file
from seed.profiles import get_profile

import logging
logger = logging.getLogger(__name__)

import os
import datetime
import json
import random
import time
import urllib
from socket import timeout as socket_timeout

def seed_machine(seed_profile):
    """
    Returns the UUID, as the object generated is pretty much
        out of flux with the remote service.

    @param: seed_profile[seed.profile.profile]

    raises:
        SeedZeroNameError
        SeedAMIDoesNotExistError

    returns:
        uuid<str> of seeded machine

    """
    conn = None
    img = None
    
    if not hasattr(seed_profile, 'name') or seed_profile.name is None:
        raise SeedZeroNameError

    ex_args = {}
    if seed_profile.driver == 'aws':
        conn = get_driver(Provider.EC2)(settings.AWS_ACCESS, 
            settings.AWS_SECRET)
        try:
            img = conn.list_images(ex_image_ids=[seed_profile.ami])[0]
        except IndexError:
            raise SeedAMIDoesNotExistError
        
        locate_security_group(img.driver, seed_profile, auto_create=True)
        import_keypair(img.driver, seed_profile, overwrite=False)

        #generate_keypair(img.driver, seed_profile)
        ex_args.update({
            'ex_region': get_availability_zone(img, seed_profile),
            #'ex_region': get_or_create_availabilty_zones(img, seed_profile),
            'ex_keyname': seed_profile.keypair.name,
            'ex_securitygroup': seed_profile.security_group.name})

    # if 'rackspace'
    size = obtain_size(img, seed_profile)
    ex_args.update({
        'name': seed_profile.name,
        'size': size,
        'image': img})
    
    current_nodes = [node.name for node in img.driver.list_nodes()]
    if seed_profile.name in current_nodes:
        raise SeedDuplicateNameError("Each node must have a unique name")

    try:
        instance = img.driver.create_node(**ex_args)
    except Exception,e:
        logger.error(e)
        if settings.DEBUG:
            raise e
    
    return instance.id

def execute_files_on_minion(deployment_files, libcloud_node, ssh_client):
    def obtain_session(ssh_client):
        channel = ssh_client.client.get_transport().open_session()
        channel.get_pty()
        channel.settimeout(settings.NETWORK_TIMEOUT)
        channel.settimeout(int(settings.NETWORK_TIMEOUT))
        return channel

    def execute_command_for_session(command, tty_session):
        logger.debug("Running command: %s" % command)
        tty_session.exec_command(command)
        while  True:
            data = tty_session.recv(131072)
            try:
                if not data:
                    break
                # if data == str('') or data == '' or not data:
                #     break
            except UnicodeError, error:
                logger.error(error)
            logger.debug(data)

    for deployment_file in deployment_files:
        if hasattr(deployment_file, 'target'):
            session = obtain_session(ssh_client)
            command = "chmod 755 %s" % deployment_file.target
            execute_command_for_session(command, session)

            session = obtain_session(ssh_client)
            execute_command_for_session(deployment_file.target, session)

            session = obtain_session(ssh_client)
            command = "chmod 444 %s" % deployment_file.target
            execute_command_for_session(command, session)

def generate_vinewhip_deployment_scripts():
    from seed.utils.rendering import generate_deploy_keys_bootstrap_script, \
        generate_source_keyfile, decorate_shell_with_keyfile, \
        generate_vinewhip_deployment_scripts, \
        generate_vinewhip_instance, generate_postgresql_env, \
        generate_vinewhip_env_standup, \
        generate_nginx_env
    scripts = []
    scripts.append(find_script('bootstrap_python_env.sh')) # Setup virtual env
    scripts.append(generate_deploy_keys_bootstrap_script()) # setup request
    scripts.append(generate_source_keyfile())
    scripts.append(decorate_shell_with_keyfile())
    scripts.append(generate_vinewhip_deployment_keys()) # setup deploy-keys
    scripts.append(generate_vinewhip_instance()) # setup vinewhip
    scripts.append(generate_postgresql_env())
    scripts.append(generate_vinewhip_env_standup())
    scripts.append(generate_nginx_env())
    # setup leechseed
    return scripts

def empower_node_with_salt_mastery(libcloud_node):
    driver = libcloud_node.driver
    logger.debug("Generating deployment script")
    scripts = generate_vinewhip_deployment_scripts()
    msd = MultiStepDeployment([FileDeployment(script, 
        target="/tmp/%s" % script.split('/')[-1:][0]) 
            for script in scripts])

    deploy_msd_to_node(libcloud_node, msd)


def water_machines(seed_profile, uuids):
    """
    Bootstrap with salt
    """
    nodes = []
    if seed_profile.driver == 'aws':
        driver = obtain_driver(seed_profile)
        nodes = driver.list_nodes(ex_node_ids=uuids)

    for libcloud_node in nodes:
        logger = logging.getLogger('*'.join([__name__, libcloud_node.name]))
        libcloud_node, private_ips = libcloud_node.driver.wait_until_running(
            nodes=[libcloud_node], ssh_interface="private_ips")[0]

        scripts = []
        for script in seed_profile.init_scripts:
            logger.warn("SCRIPT: %s" % script)
            _file = FileDeployment(find_script(script),
                target="/home/%s/%s" % (seed_profile.ami_user, script), )
            scripts.append(_file)
        msd = MultiStepDeployment(scripts)
        deploy_msd_to_node(libcloud_node, msd, seed_profile.keypair.local_path)

def deploy_msd_to_node(libcloud_node, msd, private_key_path=None):
    ##msd = MultiStepDeployment(Scripts from water_machines above)
    logger.warn("TODO: REFACTOR AND TAKE OUT ec2-user literal")
    logger.warn("TODO: ABSTRACT salt-cloud-dev.pem and cloud files to keys.sh")
    seed_profile = settings.operation_profile
    seed_profile = get_profile(seed_profile)
    pkey = seed_profile.keypair.local_path
    ssh_client = SSHClient(hostname=libcloud_node.public_ip[0],
        port=settings.SSH_PORT,
        username='ec2-user', 
        password=None,
        key=pkey,
        timeout=int(settings.NETWORK_TIMEOUT),)

    attempts = 0
    ##This begins a series of file placements for the masters subsequent deployment tasks in the init script. 
    while True:
        time.sleep(5)
        if seed_profile.profile_name == "salt_master": 
            dns_attempts = 0
            logger.info("Number of attempts to connect: %s" % dns_attempts)
            try:
                logger.info("Attemping to connect to new node.")
                ssh_client.connect() 
                logger.info("DNS SSH connection successful")
            except Exception as error:
                logger.info("DNS register ssh connection failed, trying again")
                dns_attempts += 1
                if dns_attempts > 10:
                    logger.error("DNS process failed to make a connection. Exiting.")
                    break
                continue
            # salt-cloud files necessary for deployment
            for f in seed_profile.salt_cloud_files:
                try:
                    cloud_files = FileDeployment(find_script(f),
                        target="/home/%s/%s" % (seed_profile.ami_user, os.path.basename(f)))
                    cloud_files.run(libcloud_node, ssh_client)
                    logger.info("salt-cloud file %s placed in home directory" % f)
                except Exception as e:
                    logger.error("could not place salt-cloud file: %s" % e)
            # places private key from path specified in keys.sh
            try:
                git_key = seed_profile.git_rsa_key
                git_key_file = FileDeployment(git_key,
                target= "/home/%s/%s" % (seed_profile.ami_user, os.path.basename(git_key)))
                git_key_file.run(libcloud_node, ssh_client)
                logger.info("Placed %s." % git_key_file.target)
            except Exception as e:
                logger.error("Could not place file: %s" % e)
            # places DNS registration files for the master to add itself to route 53
            try:
                try_script = find_script(seed_profile.DNS_script)
                dns_file = FileDeployment(try_script, 
                target="/home/%s/%s" % (seed_profile.ami_user, os.path.basename(try_script)) )
                dns_file.run(libcloud_node, ssh_client)
                logger.info("Placed %s ." % dns_file.target)
            except Exception as e:
                logger.error("Could not place file: %s" % e)
                 
            try:
                dns_command = find_script(seed_profile.DNS_command)
                domain = seed_profile.r53_domain
                r53_key = seed_profile.r53_key
                r53_secret = seed_profile.r53_secret
                w_command = open(dns_command, 'w')
                w_command.write("sudo python register_master_DNS.py '%(domain)s' '%(r53_key)s' '%(r53_secret)s'" % 
                    {'domain': domain,
                    'r53_key': r53_key,
                    'r53_secret': r53_secret})

                w_command.close()
                c_deploy = FileDeployment(dns_command,
                    target="/home/%s/%s" % (seed_profile.ami_user, 
                        os.path.basename(dns_command)) )
                c_deploy.run(libcloud_node, ssh_client)
                r_command = open(dns_command, 'w')
                r_command.write("""
                #This file get's blanked by the code to keep the keys out.\n 
                echo 'The DNS register command did not make it to this file.'""" )
                r_command.close()
                logger.info("The command file is in place")
                break
            except Exception as error:
                logger.error("Deployment of the DNS register file failed: %s", error)
                break
        else:
            print "%s isn't a master." % seed_profile.profile_name
            logger.warn("%s isn't a master." % seed_profile.profile_name)
            break
    ##This beings the deployment of init_scripts from water_machines
    while True:
        time.sleep(5)
        try:
            if ssh_client.connect() is True:
                # Deploy files to libcloud_node
                msd.run(libcloud_node, ssh_client)
                pubkey_file = find_script('master_public_keys.sh')
                ssh_key = get_public_key_from_file(pubkey_file)
                ssh_key.run(libcloud_node, ssh_client)

                for failed_step in msd.steps:
                    try:
                        execute_files_on_minion([failed_step], libcloud_node, ssh_client)
                    except socket_timeout, timeout:
                        logger.debug(timeout)
                        # We'll have to have the minion ping the master 
                        #   when it's alive and kicking so that we can confirm it's alive.
                        #   maybe via a webhook. 
                        # This happens when scripts you've implemented take to 
                        #   long to complete.
                        break

                    except Exception, error:
                        logger.error(error.message)
                        
                
                ssh_client.close()
            break
        except socket_timeout, timeout:
            logger.debug(timeout)

        except Exception, error:
            for earg in error.args:
                if isinstance(earg, (str, unicode)):
                    if earg.lower().find('connection refused') > -1:
                        logger.debug("%s -- %d" %(error.args, attempts))
                    elif earg.lower().find('timed out') > -1:
                        logger.debug("%s -- %d -- timeout" % (error.args, attempts))
                    elif earg.lower().find('connection closed') > -1:
                        logger.debug("%s -- %d -- connection closed" % (error.args, attempts))
                    else:
                        logger.error("%s: %s" % (error.__class__, error.args))
        
        attempts += 1
        if attempts > 10:
            break

    ssh_client.close()    

def terminate_node(libcloud_node):
    pass

def kill_machines(seed_profile, uuids=[], destroy_volume=False):
    """
    Remove the machine
    """

    if seed_profile.driver == 'aws':
        nodes = obtain_aws_nodes(uuids)
        results = []
        for node in nodes:
            if destroy_volume:
                raise NotImplementedError("Destroying Volumn is not implemented")
            results.append(node.destroy())

        return results

def freeze_machines(seed_profile, uuid):
    """
    Suspend or turn off the machine.
    """

    if seed_profile.driver == 'aws':
        nodes = obtain_aws_nodes(uuids)
        return [node.driver.ex_stop_node(node) for node in nodes]

def reanimate_machines(seed_profile, uuids=[]):
    """
    Resume a suspended machine
    """
    if seed_profile.driver == 'aws':
        nodes = obtain_aws_nodes(uuids)
        return [node.driver.ex_start_node(node) for node in nodes]

def detect_frozen_machines(seed_profile, uuids=[]):
    """
    Finds machines that are suspended.
    returns a list of uuids
    """

    ex_args = {}
    if seed_profile.driver == 'aws':
        conn = get_driver(Provider.EC2)(settings.AWS_ACCESS, 
            settings.AWS_SECRET)
        if uuids:
            nodes = conn.list_nodes(ex_node_ids=uuids)
        else:
            nodes = conn.list_nodes()

        nodes = obtain_aws_nodes(uuids)
        return [node.id
            for node in nodes 
                if node.extra.get('status') == 'stopped']


def detect_stranded_volumes(seed_profile, region=None):
    """
    Finds and reports suspended volumes
    """
    if seed_profile.driver == 'aws':
        driver = get_driver(Provider.EC2)(settings.AWS_ACCESS, 
            settings.AWS_SECRET)
        raise NotImplementedError

def expose_machines(seed_profile, uuids=[]):
    driver = obtain_driver(seed_profile)
    
    if uuids:
        return driver.list_nodes(uuids)

    return driver.list_nodes()
