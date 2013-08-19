# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import sys
import os
import argparse
import re

"""
File: parse_launch_name.py
Author: Jon Slusher
Email: jonslusher@gmail.com
Github: 
Description: 
"""
grn_inf_dict = {
        'aws': 'aws',
        'xen': 'xenserver',
        'rak': 'rackspace',
        'gov': 'govcloud'
        }
grn_env_dict = {
        'dev': 'dev',
        'prd': 'prod',
        'stg': 'stage'
        }

grn_srvgrp_dict = {
        'int': 'intserver',
        'dat': 'datserver',
        'msg': 'msgserver',
        'prc': 'prcserver',
        'fes': 'feserver'
        }

grn_srvtype_dict = {
        'cin': 'contentint',
        'cfg': 'configuration',
        'mon': 'monitoring',
        'srv': 'services',
        'red': 'redis',
        'upg': 'uum_postgres',
        'spg': 'sen_postgres',
        'dpg': 'dja_postgres',
        'gpg': 'gen_postgres',
        'prx': 'proxy'
        }

grn_srvrole_dict = {
        'bbt': 'buildbot',
        'gtr': 'git_repo',
        'ymr': 'yum_repo',
        'pyr': 'pypi_repo',
        'slm': 'salt_master',
        'grp': 'graphite',
        'rsl': 'rsyslog',
        'sen': 'sentry',
        'kib': 'kibana',
        'lgs': 'logstash',
        'std': 'statsd',
        'dns': 'dns',
        'ntp': 'ntp',
        'pgm': 'pg_master',
        'pgs': 'pg_slave',
        'gpp': 'graphite_pxy',
        'opp': 'olpub_pxy',
        'pgp': 'pg_pool'
        }

prof_dict = {
        'ec2_e_mic': 'ec2_east_micro',
        'ec2_w_mic': 'ec2_west_micro',
        'ec2_e_med': 'ec2_east_medium',
        'ec2_w_med': 'ec2_west_medium',
        'ec2_e_lar': 'ec2_east_large',
        'ec2_w_lar': 'ec2_west_large',
        'ec2_e_lml': 'ec2_east_aws_linux_mem_large',
        'ec2_e_rml': 'ec2_east_rhel_mem_large',
        }


parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file', type=str, 
                    dest='hostname_file', 
                    help="specify file to read hostnames")
parse_args = parser.parse_args()
hostname_file =  parse_args.hostname_file


def parse_instance_name(hostname=None, profile='ec2_east_micro'):
    if 'ec2' in hostname:
        with open('map_file', 'a') as pfile:
            pfile.write("%(p)s:\n" % {'p': prof_dict[hostname]})
    else:
        hostname_split = hostname.split('-') or hostname.split('_')
        for grain in hostname_split:
            if len(grain) > 3:
                grain = grain.strip(grain[3:])
            if grain in grn_inf_dict:
                inf = grain
            elif grain in grn_env_dict:
                env = grain
            elif grain in grn_srvgrp_dict:
                grp = grain
            elif grain in grn_srvtype_dict:
                typ = grain
            elif grain in grn_srvrole_dict:
                rle = grain
            else:
                print "\n!!! '%s' is not a grain. Check the spreadsheet and \
                        verify you typed it correctly. !!!\n" % grain
                exit(1)
        try:
            with open('map_file', 'a') as gfile:
                gfile.write("  - %(h)s: \n"
                            "      grains: \n"
                            "        infrastructure: %(i)s \n"
                            "        environment: %(e)s \n"
                            "        servergroup: %(g)s \n"
                            "        servertype: %(t)s \n"
                            "        serverrole: %(r)s \n" % {
                                    'p': profile,
                                    'h': hostname,
                                    'i': grn_inf_dict[inf],
                                    'e': grn_env_dict[env], 
                                    'g': grn_srvgrp_dict[grp], 
                                    't': grn_srvtype_dict[typ],
                                    'r': grn_srvrole_dict[rle]
                                    })
            print "grains written to map file map_file"
        except UnboundLocalError as e:
            print ">could not write grains to file: || %s" % e
            print ">you must have one grain from each of the 5 categories."
            exit(1)

if __name__ == '__main__':
    clean_file = open('map_file', 'w')
    clean_file.write('')
    clean_file.close()
    
    if hostname_file:
        hostname_file = open(hostname_file, 'r')
        for i in hostname_file:
            parse_instance_name(hostname=i[:-1])
    else:
        arg_list = sysargv[1:]
        for i in arg_list:
            parse_instance_name(hostname=i)
    exit(0)
