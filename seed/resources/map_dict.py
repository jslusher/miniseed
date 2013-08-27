# -*- coding: utf-8 -*-

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
        'rep': 'repo',
        'prx': 'proxy',
        'pgm': 'pg_master',
        'pgs': 'pg_slave',
        'pgp': 'pg_pool'
        }

grn_srvrole_dict = {
        'bbt': 'buildbot',
        'gtr': 'git_repo',
        'yum': 'yum_repo',
        'pyr': 'pypi_repo',
        'red': 'redis',
        'slr': 'solr',
        'stm': 'storm',
        'slm': 'salt_master',
        'grp': 'graphite',
        'rsl': 'rsyslog',
        'sen': 'sentry',
        'dns': 'dns',
        'ntp': 'ntp',
        'upg': 'uum_postgres',
        'spg': 'sen_postgres',
        'dpg': 'dja_postgres',
        'gpg': 'gen_postgres',
        'gpp': 'graphite_pxy',
        'opp': 'olpub_pxy',
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
