# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from seed.profiles.aws.constants import i386 as AWS_i386
from seed.profiles.aws.constants import x86_64 as AWS_x86_64
import os
import json
from seed import settings

domain = "dev.next.opinionlab.com."
route53_key = settings.ROUTE53_KEY
route53_secret = settings.ROUTE53_SECRET

master_profile = {
    "profile_name": "salt_master",
    "driver": AWS_x86_64.driver,
    "ami": AWS_x86_64.ami,
    "ami_user": AWS_x86_64.user,
    "ami_group": AWS_x86_64.group,
    "keypair": {
        "name": "salt-dev-jon",
        "local_path": os.path.expanduser("~/.ssh/olab/salt-dev-jon"),
        "bits": 4096,
    },
    "verbose": 3,
    "security_group": {
        "name": "salt-dev-jon",
        "description": "auto-generated",
        "ports": [
            {
            "from_port": "22",
            "to_port": None,
            "protocol": "tcp",
            "cidr_ip": "0.0.0.0/0",
            },{
            "from_port": "4505",
            "to_port": None,
            "protocol": "tcp",
            "cidr_ip": "0.0.0.0/0",
            },{
            "from_port": "4506",
            "to_port": None,
            "protocol": "tcp",
            "cidr_ip": "0.0.0.0/0",
            },{
            "from_port": "4511",
            "to_port": None,
            "protocol": "tcp",
            "cidr_ip": "0.0.0.0/0",
            },{
            "from_port": "4510",
            "to_port": None,
            "protocol": "tcp",
            "cidr_ip": "0.0.0.0/0",
            },{
            "from_port": "8000",
            "to_port": None,
            "protocol": "tcp",
            "cidr_ip": "0.0.0.0/0",
            }
        ]
    },
    "region": "us-east-1d",
    "size": "t1.micro",
    "tags": ["master", "dev", "salt"],
    "init_scripts": ["master_init.sh",
                    "development_tools_group_install.sh",
                    "postgres_install.sh"],
    "DNS_script": "seed/resources/register_master_DNS.py",
    "DNS_command": "seed/resources/r53_register_command.sh",
    "r53_domain": domain,
    "r53_key": route53_key,
    "r53_secret": route53_secret
    }

minion_profile = master_profile.copy()
minion_profile.update({
    "profile_name": "salt-minion-i386",
    "keypair": {
        "name": "salt-dev-minion",
        "local_path": os.path.expanduser("~/.ssh/olab/salt-dev-minion"),
        "bits": 4096,
    },
    "tags": ['minion', 'dev', 'salt'],
    "init_scripts": ["minion_init.sh"]
    })


minion64_profile = master_profile.copy()
minion64_profile.update({
    "profile_name": "salt-minion-x86_64",
    "keypair": {
        "name": "salt-dev-minion",
        "local_path": os.path.expanduser("~/.ssh/olab/salt-dev-minion"),
        "bits": 4096,
    },
    "tags": ['minion', 'dev', 'salt'],
    "init_scripts": ["minion_init.sh"],
    "driver": AWS_x86_64.driver,
    "ami": AWS_x86_64.ami,
    "ami_user": AWS_x86_64.user,
    "ami_group": AWS_x86_64.group
    })


available_profiles = {
    'aws_master': master_profile.copy(),
    'aws_minion': minion_profile.copy(),
    'aws64_minion': minion64_profile.copy(),
    }

