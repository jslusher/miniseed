# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import sys
import os
import argparse
import re
import logging

from seed.utils.api import find_script
from seed.utils import map_dict

logger = logging.getLogger(__name__)

salt_cloud_map = find_script('salt_cloud_map')

def parse_instance_name(hostname=None, profile='ec2_east_micro'):
    if 'ec2' in hostname:
        with open(salt_cloud_map, 'a') as pfile:
            pfile.write("%(p)s:\n" % {'p': map_dict.prof_dict[hostname]})
    else:
        hostname_split = hostname.split('-') or hostname.split('_')
        for grain in hostname_split:
            if len(grain) > 3:
                grain = grain.strip(grain[3:])
            if grain in map_dict.grn_inf_dict:
                inf = grain
            elif grain in map_dict.grn_env_dict:
                env = grain
            elif grain in map_dict.grn_srvgrp_dict:
                grp = grain
            elif grain in map_dict.grn_srvtype_dict:
                typ = grain
            elif grain in map_dict.grn_srvrole_dict:
                rle = grain
            else:
                logger.error("\n!!! '%s' is not a grain. Check the spreadsheet and \
                        verify you typed it correctly. !!!\n" % grain)
                exit(1)
        try:
            with open(salt_cloud_map, 'a') as gfile:
                gfile.write("  - %(h)s: \n"
                            "      grains: \n"
                            "        infrastructure: %(i)s \n"
                            "        environment: %(e)s \n"
                            "        servergroup: %(g)s \n"
                            "        servertype: %(t)s \n"
                            "        serverrole: %(r)s \n" % {
                                    'p': profile,
                                    'h': hostname,
                                    'i': map_dict.grn_inf_dict[inf],
                                    'e': map_dict.grn_env_dict[env], 
                                    'g': map_dict.grn_srvgrp_dict[grp], 
                                    't': map_dict.grn_srvtype_dict[typ],
                                    'r': map_dict.grn_srvrole_dict[rle]
                                    })
            logger.info("grains written to map file %s" % salt_cloud_map)
        except UnboundLocalError as e:
            logger.error("could not write grains to file: || %s" % e)
            logger.error("you must have one grain from each of the 5 categories.")
            exit(1)

def parse_map_file(map_file):
    clean_file = open(salt_cloud_map, 'w')
    clean_file.write('')
    clean_file.close()
    
    hostname_file = open(map_file, 'r')
    for i in hostname_file:
        parse_instance_name(hostname=i[:-1])
