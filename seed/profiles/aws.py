# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import json

master_profile = {
    "driver": "aws",
    "ami": "ami-6f640c06", #"ami-dd3758b4", #ami-0d44cd64",
    "ami_user": "ec2-user",
    "ami_group": "www-data",
    "keypair": {
        "name": "salt-dev",
        "local_path": os.path.expanduser("~/.ssh/olab/salt-dev"),
        "bits": 4096,
    },
    "verbose": 3,
    "security_group": {
        "name": "salt-dev",
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
                    # "install_m2crypto.sh",
                    "development_tools_group_install.sh",
                    "postgres_install.sh", ],
    }

minon_profile = master_profile.copy()
minon_profile.update({
    "keypair": {
        "name": "salt-dev-minion",
        "local_path": os.path.expanduser("~/.ssh/olab/salt-dev-minion"),
        "bits": 4096,
    },
    "tags": ['minion', 'dev', 'salt'],
    "init_scripts": ["minion_init.sh"]
    })

available_profiles = {
    'aws_master': master_profile.copy(),
    'aws_minion': minon_profile.copy(),
    }

