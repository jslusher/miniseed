# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from seed import settings
from seed.profiles import aws, get_profile
from seed.utils import seed_machine, water_machines, \
    expose_machines, seed_vpc
from seed.utils.parse_map_file import parse_map_file
from seed.exceptions import SeedProfileDoesNotExistError, \
    SeedZeroNameError, SeedMachineDoesNotExistError, SeedDomainExistError, \
    SeedDomainDoesNotExistError, SeedInvalidCredentials, \
    SeedMasterIsNotMinionError

import logging
logger = logging.getLogger(__name__)

import os
import sys

from libcloud.dns.providers import get_driver as get_dns_driver
from libcloud.dns.types import Provider as DNSProvider, RecordType

def run():
    actions = {
        'list_ips': list_ips,
        'list': list_nodes,
        'launch': create,
        'terminate': terminate,
    }
    
    if settings.action not in actions:
        raise AttributeError("%s does not exist.[%s]"
            % (settings.action, ', '.join(actions.keys())))

    action = actions.get(settings.action)
    action()

def create(instance_name=None):
    """
    Spin up new instances.
    Display all running instances.

    raises:
        profiles.exceptions.MissingProfileNameError
        profiles.exceptions.DriverNotSupportedError
    """
    if settings.operation_profile_list:
        p_list = ','.join(SEED_PROFILES.keys())
        for p in p_list:
            logger.info("Profile: %s" % p)
        #logger.info("Profiles: [%s]" % ','.join(SEED_PROFILES.keys()))
        sys.exit()

    if settings.operation_profile:
        seed_profile = get_profile(settings.operation_profile)
    else:
        settings.operation_profile = "salt_master"
        seed_profile = aws.master_profile.copy()
        logger.info("Using default profile: %s " % settings.operation_profile)
    
    if not seed_profile: 
        raise SeedProfileDoesNotExistError("%s" % settings.operation_profile)
    
    if settings.map_list:
        parse_map_file(settings.map_list)
    else:
        logger.info("map_file not specified. using existing salt_cloud_map file from resources.")
    logger.info("Profile being used: %s" % settings.operation_profile)
    seed_profile.name = instance_name or settings.name
    if settings.vpc_subnet:
        instance_id = seed_vpc(seed_profile)
    else:
        instance_id = seed_machine(seed_profile)
    water_machines(seed_profile, [instance_id])

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

def terminate(instance_name=None):
    """
    Destroy node and all minion nodes.

    This is dangerious. 
    """
    
    # $ python -m seed -a terminate -n [name]
    instance_name = instance_name or settings.name
    if instance_name is None:
        raise SeedZeroNameError("You must specify a name to terminate a salt master")

    salt_master = aws.AWS_MASTER.copy()
    libcloud_nodes = expose_machines(salt_master)
    for libcloud_node in libcloud_nodes:
        if libcloud_node.name == instance_name:
            terminate_node(libcloud_node)
            return True      
    

    raise SeedMachineDoesNotExistError(instance_name)


def list_nodes(silent=False):
    salt_master = aws.AWS_MASTER.copy()
    data = expose_machines(salt_master)
    if not silent:
        logger.info("Online instances:")
        inst_list = expose_machines(salt_master)
        for i in inst_list:
            logger.info("Instance: %s    IP:    %s    State:    %s    uuid: %s" % (i.name, i.public_ips, i.state, i.uuid))
    
def list_ips(node_name=None):
    salt_master = aws.AWS_MASTER.copy()
    data = expose_machines(salt_master)
    for i in data:
        try:
            print "%s <==> %s" % (i.name, i.public_ips[0])
        except IndexError as e:
            print "%s <==> %s" % (i.name, i.public_ips)
