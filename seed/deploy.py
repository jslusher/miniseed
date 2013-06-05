# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from seed import settings
from seed.profiles import available_profiles, SEED_PROFILES, get_profile
from seed.utils import seed_machine, water_machines, \
    kill_machines, freeze_machines, reanimate_machines, \
    expose_machines, empower_node_with_salt_mastery, terminate_node
from seed.utils.rendering import generate_source_keyfile
from seed.utils.salt import attach_minion_to_master
from seed.shortcuts import obtain_driver_by_name
from seed.exceptions import SeedProfileDoesNotExistError, \
    SeedZeroNameError, SeedMachineDoesNotExistError, SeedDomainExistError, \
    SeedDomainDoesNotExistError, SeedInvalidCredentials, \
    SeedMasterIsNotMinionError

import logging
logger = logging.getLogger(__name__)

import os
import shutil
import zipfile

from libcloud.dns.providers import get_driver as get_dns_driver
from libcloud.dns.types import Provider as DNSProvider, RecordType

def run():
    actions = {
        'list': list_nodes,
        'launch': create,
        'empower': empower,
        'terminate': terminate,
        'register-domain': register_domain,
        'remove-domain': remove_domain_for_machine,
        'package-deploy-keys': package_deploy_keys,
        'install-deploy-keys': install_deploy_keys,
        'generate-keys-file': generate_keys_file,
        'attach-minions': attach_minions,
    }
    
    if settings.action not in actions:
        raise AttributeError("%s does not exist.[%s]"
            % (settings.action, ', '.join(actions.keys())))

    action = actions.get(settings.action)
    action()

def generate_keys_file(seed_profile=None):
    
    seed_profile = seed_profile or settings.operation_profile
    seed_profile = get_profile(seed_profile)
    script_path = settings.output_path or os.path.join(os.path.dirname(__file__), 'keys.sh')
    values = {
        'unix_user': seed_profile.ami_user,
        'unix_group': seed_profile.ami_group,
        }

    while True:
        raw_data = raw_input("\nInput your AWS_ACCESS key: ")
        if raw_data != '' and not None:
            break
    values.update({
        'AWS_ACCESS':raw_data})
    while True:
        raw_data = raw_input("\nInput your AWS_SECRET key: ")
        if raw_data != '' and not None:
            break
    values.update({
        'AWS_SECRET':raw_data})
    
    logger.info("Testing Access Keys...")
    settings.AWS_ACCESS = values.get('AWS_ACCESS')
    settings.AWS_SECRET = values.get('AWS_SECRET')
    try:
        list_nodes(silent=True) 
    except Exception:
        raise SeedInvalidCredentials

    while True:
        raw_data = raw_input("\nGive a domain specific name for this cluster: ")
        if raw_data != '' and not None:
            break
    settings.name = raw_data

    logger.info("Building Keyfile")
    raw_data = 'n'
    if os.path.exists(script_path):
        ACCEPTABLE_INPUT = ['y','Y','n','N']
        while True:
            raw_data = raw_input("keys file exists there, would you like to ovrewrite it? [n/Y] ")
            if raw_data in ACCEPTABLE_INPUT:
                break
        if raw_data in ['n', 'N']:
            logger.info("Aborted")
            import sys; sys.exit(1)

        os.remove(script_path)
            
    logger.info("Writing keyfile to %s" % os.path.abspath(script_path))
    generate_source_keyfile(script_path=script_path, **values) 

def install_deploy_keys(seed_profile=None, zip_archive=None):
    
    seed_profile = seed_profile or settings.operation_profile
    if seed_profile is None:
        raise SeedProfileMissing("You must pass a profile [-p aws_master]")

    seed_profile = get_profile(seed_profile)

    zip_archive = zip_archive or settings.key_import_path
    if zip_archive is None or not os.path.exists(zip_archive):
        raise IOError("zip zip_archive is missing [ -i %s] " % zip_archive)

    dir_path = os.path.dirname(seed_profile.keypair.local_path)
    if os.path.exists(os.path.dirname(seed_profile.keypair.local_path)):
        ACCEPTABLE_INPUT = ['y', 'Y', 'n', 'N']
        data = None
        while data not in ACCEPTABLE_INPUT:
            data = raw_input('\n%s keypair exists, would you like to overwrite it? [y/N]' % seed_profile.keypair.name)

        if data in ['N', 'n']:
            import sys
            sys.exit()

        logger.info("Overwriting [%s]" %seed_profile.keypair.local_path)
        shutil.rmtree(dir_path)
    
    os.makedirs(dir_path)

    with zipfile.ZipFile(zip_archive, 'r') as stream:
        for item in stream.infolist():
            declaird_filename = item.filename.split('/')[-1:][0]
            new_file_path = os.path.join(dir_path, declaird_filename)
            with open(new_file_path, 'wb+') as file_stream:
                file_stream.write(stream.read(item.filename))

            if new_file_path.endswith('.pub'):
                os.chmod(new_file_path, 0644)
            else:
                os.chmod(new_file_path, 0600)


    logger.info("Keys installed in [%s]" % dir_path)


def package_deploy_keys(seed_profile=None):

    seed_profile = seed_profile or settings.operation_profile
    if seed_profile is None:
        raise SeedProfileMissing("You must pass a profile [-p aws_master]")

    seed_profile = get_profile(seed_profile)
    zip_path = settings.key_export_path or "/tmp/%s.zip" % seed_profile.keypair.name
    temp_key_dir_path = "/tmp/%s" % seed_profile.keypair.name
    private_key_path = seed_profile.keypair.local_path
    temp_private_key_path = "/tmp/%s/%s" % (seed_profile.keypair.name, seed_profile.keypair.name)
    public_key_path = "%s.pub" % seed_profile.keypair.local_path
    temp_public_key_path = "/tmp/%s/%s.pub" % (seed_profile.keypair.name, seed_profile.keypair.name)

    if os.path.exists(temp_key_dir_path):
        shutil.rmtree(temp_key_dir_path)
    os.makedirs(temp_key_dir_path)
    shutil.copyfile(private_key_path, temp_private_key_path)
    shutil.copyfile(public_key_path, temp_public_key_path)

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_STORED) as stream:
        stream.write(temp_private_key_path)
        stream.write(temp_public_key_path)

    logger.info("Key files zipped and placed [%s]" % zip_path)
    logger.info("gpg encode this archive before you send it to anyone. If you don't...")
    logger.info("gpg -e -a -r jcurtin@opinionlab.com -o /tmp/key_archive.zip.asc /path/to/key_archive")


def remove_domain_for_machine(instance_name=None, provider_name=None, requested_domain=None, attach_to_zone=None):
    """
    python -m seed -a remove-domain --provider aws -n bulbasaur
    """
    instance_name = instance_name or settings.name
    if instance_name is None:
        raise SeedZeroNameError("You must specify a name to terminate a salt master")

    provider_name = provider_name or settings.provider
    requested_domain = requested_domain or settings.domain or '.'.join([instance_name,settings.DNS_DEFAULT])
    attach_to_zone = attach_to_zone or settings.DNS_DEFAULT

    if not requested_domain.endswith('.'):
        requested_domain = '%s.' % requested_domain
    driver = obtain_driver_by_name(provider_name)

    instance = get_instance_by_name(instance_name)
    if instance is None:
        raise SeedMachineDoesNotExistError(instance_name)

    record_or_zone = obtain_domain_record(requested_domain)
    if record_or_zone is None:
        raise SeedDomainDoesNotExistError(requested_domain)

    logger.info("Removing %s" % record_or_zone)
    record_or_zone.delete()
    logger.info("Removed %s" % requested_domain)



def get_instance_by_name(instance_name, seed_profile=None):
    if seed_profile is None:
        seed_profile = available_profiles.AWS_MASTER.copy()

    for libcloud_node in expose_machines(seed_profile):
        if libcloud_node.name == instance_name:
            return libcloud_node

    return None

def obtain_domain_record(requested_domain, seed_profile=None):
    dns_driver = get_dns_driver(DNSProvider.ROUTE53)(settings.AWS_ACCESS, settings.AWS_SECRET)
    record_types = {}
    [record_types.update({value:key}) for key,value in RecordType.__dict__.copy().iteritems() if not key.startswith('_') and value.__class__ == int]

    record_names = []

    for zone in dns_driver.list_zones():
        if zone.domain.lower() == requested_domain.lower():
            return zone

        for record in zone.list_records():
            if record_types.get(record.type) == 'CNAME' or record_types.get(record.type) == 'A':
                # Because route53 is special, it encodes all * to \\052 ( utf-8 )
                if record.name == '\\052':
                    record_domain = '*.%s' % zone.domain
                else:
                    record_domain = '.'.join([record.name.encode('utf-8'), zone.domain])

                if record_domain == requested_domain.lower().encode('utf-8'):
                    return record

    return None

def does_domain_record_exist(requested_domain, seed_profile=None):
    """
    Raises SeedDomainExistError if the domain does not exist
    """
    record_or_zone = obtain_domain_record(requested_domain, seed_profile)
    if record_or_zone is not None:
        raise SeedDomainExistError(requested_domain.lower())


def register_domain(instance_name=None, provider_name=None, requested_domain=None, attach_to_zone=None, auto_create_zone=False):
    """
    instance_name: alpha0
    provider_name: aws
    requested_domain: awesome_sauce.napperjabber.com
    attach_to_zone: napperjabber.com
    auto_create_zone: False # Auto creates "attach_to_zone"

    python -m seed -a register-domain -n alpha0 --provider aws -d awesome_sauce.napperjabberlabs.com
    awesome_sauce.napperjabberlabs.com -> x.x.x.x

    python -m seed -a register-domain --provider aws -n alpha0
    alpha0.napperjabberlabs.com

    """

    # alpha0-int.napperjabberlabs.com
    # $ python -m seed -a register-domain -n [name]
    instance_name = instance_name or settings.name
    if instance_name is None:
        raise SeedZeroNameError("You must specify a name to terminate a salt master")

    provider_name = provider_name or settings.provider
    requested_domain = requested_domain or settings.domain or '.'.join([instance_name,settings.DNS_DEFAULT])
    attach_to_zone = attach_to_zone or settings.DNS_DEFAULT

    if not requested_domain.endswith('.'):
        requested_domain = '%s.' % requested_domain
    driver = obtain_driver_by_name(provider_name)

    instance = get_instance_by_name(instance_name)
    if instance is None:
        raise SeedMachineDoesNotExistError(instance_name)
    
    does_domain_record_exist(instance_name)

    dns_driver = get_dns_driver(DNSProvider.ROUTE53)(settings.AWS_ACCESS, settings.AWS_SECRET)
    operating_zone = None
    for zone in dns_driver.list_zones():
        if zone.domain == attach_to_zone:
            operating_zone = zone

    if operating_zone is None and auto_create_zone:
        operating_zone = dns_driver.create_zone(domain=requested_domain)

    requested_domain = requested_domain.split(operating_zone.domain)[0]
    if requested_domain.endswith("."):
        requested_domain = requested_domain[:len(requested_domain)-1]

    operating_zone.create_record(requested_domain, 
        RecordType.A, 
        instance.public_ips[0], extra={"ttl": 300})
    operating_zone.create_record("%s-int" % requested_domain,
        RecordType.CNAME,
        instance.extra.get('dns_name'), extra={"ttl": 43200})

    logger.info("Created [%s] points to [%s]" % 
        ('.'.join([requested_domain,settings.DNS_DEFAULT]), instance.public_ips[0]))
    logger.info("[%s] points to [%s]" %
        ('.'.join(["%s-int" % requested_domain, settings.DNS_DEFAULT]), instance.extra.get('dns_name')))

def terminate(instance_name=None):
    """
    Destroy node and all minion nodes.

    This is dangerious. 
    """
    
    # $ python -m seed -a terminate -n [name]
    instance_name = instance_name or settings.name
    if instance_name is None:
        raise SeedZeroNameError("You must specify a name to terminate a salt master")

    salt_master = available_profiles.AWS_MASTER.copy()
    libcloud_nodes = expose_machines(salt_master)
    for libcloud_node in libcloud_nodes:
        if libcloud_node.name == instance_name:
            terminate_node(libcloud_node)
            return True      
    

    raise SeedMachineDoesNotExistError(instance_name)

def empower(instance_name=None):

    # $ python -m seed -a empower -n [name]
    instance_name = instance_name or settings.name
    if instance_name is None:
        raise SeedZeroNameError("You must specify a name to empower a salt master")

    salt_master = available_profiles.AWS_MASTER.copy()
    libcloud_nodes = expose_machines(salt_master)
    for libcloud_node in libcloud_nodes:
        if libcloud_node.name == instance_name:
            empower_node_with_salt_mastery(libcloud_node)
            return True      
    

    raise SeedMachineDoesNotExistError(instance_name)

def attach_minions(master_instance_name=None, minion_instance_names=[]):
    master_instance_name = master_instance_name or settings.name
    minion_instance_names = minion_instance_names or settings.minion_names
    if isinstance(minion_instance_names, (str, unicode)):
        minion_instance_names = minion_instance_names.split(',')

    if master_instance_name is None:
        raise SeedZeroNameError("You must specify a name to empower a salt master.")
    if not minion_instance_names:
        raise SeedZeroNameError("You must specify atleast on minion name to attach a master [%s]" % master_instance_name)
    if master_instance_name in minion_instance_names:
        raise SeedMasterIsNotMinionError("You cannot pass the master name as a minion while attaching minions to this master.")

    exposed_nodes = {} 
    for profile_name, profile in available_profiles.copy().__dict__.iteritems():
        for machine in expose_machines(profile):
            exposed_nodes.update({machine.name: machine})
    
    if master_instance_name not in exposed_nodes.keys():
        raise SeedZeroNameError("Master name is nonexistant in cloud. [%s]" % name)
    for name in minion_instance_names:
        if name not in exposed_nodes.keys():
            raise SeedZeroNameError("Minion name is nonexistant in cloud. [%s]" % name)
 
    master_node = None
    minion_nodes = {}
    for node_name, node in exposed_nodes.items():
        if node_name == master_instance_name:
            master_node = node
            continue 
        for minion_name in minion_instance_names:
            if node_name == minion_name:
                minion_nodes.update({minion_name: node})

    logger.info("We're now tellng the minions where the master lives. This may take a while.")
    for minion_node_name, minion_node in minion_nodes.items():
        logger.info("Attaching [%s] to master: [%s]" % 
            (minion_node_name, master_node.name))
        attach_minion_to_master(libcloud_master_node=master_node,
            libcloud_minion_node=minion_node)

def create(instance_name=None):
    """
    Spin up new instances.
    Display all running instances.

    raises:
        profiles.exceptions.MissingProfileNameError
        profiles.exceptions.DriverNotSupportedError


    """
    if settings.operation_profile_list:
        logger.info("Profiles: [%s]" % ','.join(SEED_PROFILES.keys()))
        import sys;sys.exit()

    if settings.operation_profile:
        seed_profile = get_profile(settings.operation_profile)
    else:
        settings.operation_profile = "salt_master"
        seed_profile = available_profiles.AWS_MASTER.copy()
        logger.info("Using default profile: %s " % settings.operation_profile)
    
    if not seed_profile: 
        raise SeedProfileDoesNotExistError("%s" % settings.operation_profile)
    
    logger.info("Profile being used: %s" % settings.operation_profile)
    seed_profile.name = instance_name or settings.name
    instance_id = seed_machine(seed_profile)
    water_machines(seed_profile, [instance_id])

def list_nodes(silent=False):
    salt_master = available_profiles.AWS_MASTER.copy()
    data = expose_machines(salt_master)
    if not silent:
        logger.info("Online instances.")
        logger.info(expose_machines(salt_master))
    
