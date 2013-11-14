# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import logging
from seed.exceptions import SeedKeyPairDoesNotExistError, SeedException
from seed.utils.keys import generate_keypair

try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

logger = logging.getLogger(__name__)

def locate_security_group(ec2_driver, seed_profile, auto_create=False):
    """
    @param: ec2_driver[libcloud.compute.drivers.ec2.EC2NodeDriver]
    @param: seed_profile[seed.profiles.profile]
    @param: auto_create:False[boolean]

    raises:
        SecurityGroupDoesNotExistError
        
    return bool [ created = True ]

    with auto_create, it'll gracefully create a security group. 
    """
    available_security_groups = ec2_driver.ex_list_security_groups()
    if seed_profile.security_group['name'] not in available_security_groups:
        if not auto_create:
            raise SecurityGroupDoesNotExistError(seed_profile.security_group['name'])
    
    try:
        ec2_driver.ex_create_security_group(
            seed_profile.security_group['name'],
            seed_profile.security_group['description'], )
        logger.debug("Security Group already exists %s" % seed_profile.security_group['name'])
    except SeedException, e:
        raise e
    except Exception, e:
        if not e.message.startswith('InvalidGroup.Duplicate'):
            logger.error(e.message)

    return update_security_group(ec2_driver, seed_profile)

def update_security_group(ec2_driver, seed_profile):
    """
    @param ec2_driver[libcloud]
    @param seed_profile[seed.profiles.profile]

    @raise SecurityGroupDoesNotExistError

    returns boolean on success
    """
    try:
        for port in seed_profile.security_group['ports']:
            ec2_driver.ex_authorize_security_group(
                seed_profile.security_group['name'],
                port.from_port,
                port.to_port or port.from_port,
                port.cidr_ip,
                port.protocol, )
            logger.debug("Adding %s from %s to %s" 
                %(port.protocol, 
                    unicode(port.from_port), 
                    unicode(port.to_port or port.from_port)))
    except Exception, error:
        raise error

    return True

def get_availability_zone(libcloud_image, seed_profile):
    """
    @param libcloud_image[libcloud.compute.base.NodeImage]
    @param seed_profile

    raises
        SeedAvailibiltyZoneDoesNotExist
    returns libcloud.compute.drivers.ec2.ExEC2AvailabilityZone
    """
    available_zones = {}
    for zone in libcloud_image.driver.ex_list_availability_zones():
        available_zones.update({
            zone.name: zone})

    if seed_profile.region not in available_zones.keys():
        raise SeedAvailibiltyZoneDoesNotExist("%s [ %s ]" 
           % (seed_profile.region, ','.join(available_zones.keys())))
    logger.debug("Using %s region" % seed_profile.region)
    return available_zones.get(seed_profile.region)

def obtain_size(libcloud_image, seed_profile):
    """
    @param libcloud_image[libcloud.compute.base.NodeImage]
    @param seed_profile
    
    raises
        SeedSizeDoesNotExist

    returns libcloud.compute.base.NodeSize
    """
    available_sizes = {}
    for size in libcloud_image.driver.list_sizes():
        available_sizes.update({
            size.id:size})

    if seed_profile.size not in available_sizes.keys():
        raise SeedSizeDoesNotExist("%s [ %s ]"
            % (seed_profile.size, ','.join(available_sizes.keys())))
    logger.debug("Using %s size" % seed_profile.size)
    return available_sizes.get(seed_profile.size)

def import_keypair(ec2_driver, seed_profile, overwrite=False):
    """
    @param libcloud_image[libcloud.compute.base.NodeImage]
    @param seed_profile[seed.profiles.profile]
    @param overwrite:False[boolean]
    
    raises:
        SeedKeyPairExistsError

    returns boolean

    The right conditions:
    driver doesn't have the keypair

    over-writing the keypair could have drastice overhead charges
     you have to manually remove them from every running instance.
    """
    try:
        seed_keypair = ec2_driver.ex_describe_keypairs(seed_profile.keypair['name'])
        logger.debug("Keypair exists %s" % seed_profile.keypair['name'])
    except Exception as  e:
        if not error.message.startswith('InvalidKeyPair.NotFound'):
            logger.error(e.message)
    
    private_key_path, public_key_path, generated = obtain_keypair(seed_profile, overwrite=overwrite)
    if overwrite or generated:
        logger.debug("Injecting Keypair to AWS [%s]" % seed_profile.keypair.name)
        ec2_driver.ex_import_keypair(seed_profile.keypair['name'], public_key_path)

    return True

def obtain_keypair(seed_profile, overwrite=False):
    """
    @param seed_profile
    
    This method is a little tricky, as it's not d
    the right conditions:
    the keypair doesn't exist locally
    """
    generated = False
    if not os.path.exists(seed_profile.keypair['local_path']) and not os.path.exists(seed_profile.keypair['local_path']) or overwrite:
        logger.debug("Generating keypair here %s" % seed_profile.keypair['local_path'])
        private_key_path, public_key_path = generate_keypair(
            seed_profile.keypair['local_path'],
            "%s.pub" % seed_profile.keypair['local_path'],
            bits=seed_profile.keypair.bits, )
        generated = True

    return "%s" % seed_profile.keypair['local_path'], "%s.pub" % seed_profile.keypair['local_path'], generated

def apply_tags(libcloud_image, seed_profile):

    print "PAssing on appling tags....for nowe"

