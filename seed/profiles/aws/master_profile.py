from __future__ import unicode_literals
from constants import x86_64 as AWS_x86_64

import os
from seed import settings

domain = "dev-next.opinionlab.com."
route53_key = settings.ROUTE53_KEY
route53_secret = settings.ROUTE53_SECRET
git_rsa_key = settings.GIT_PKEY
salt_cloud_key = settings.SALT_CLOUD_KEY

master_profile = {
    "profile_name": "salt_master",
    "driver": AWS_x86_64.driver,
    "ami": AWS_x86_64.ami,
    "ami_user": AWS_x86_64.user,
    "ami_group": AWS_x86_64.group,
    "keypair": {
        "name": "salt-cloud-dev",
        "local_path": os.path.expanduser("~/.ssh/olab/salt-cloud/salt-cloud-dev.pem"),
        "bits": 4096,
    },
    "vpc_subnets": {
        "dev_east_1a": "subnet-0b10257f",
        "dev_east_1b": " subnet-0b17404d",
        "dev_east_1d": "subnet-61dfa849",
        },
    "verbose": 3,
    "security_group": {
        "name": "salt-dev",
        "description": "auto-generated",
            },
    "vpc_sec_grp_ids": {
        "default": ["sg-26d7cf44",],
        },
    "region": {
        "dev_east_1a": "us-east-1a",
        "dev_east_1b": "us-east-1b",
        "dev_east_1d": "us-east-1d",
        },
    "vpc_east_region": "us-east-1",
    "size": {
        "dev": "m1.small",
        "qa": "t1.micro",
        "stage": "m1.small",
        "prod": "m1.small",
        },
    "init_scripts": ("master_init.sh",),
    "salt_cloud_files": ("cloud", "cloud.profiles", "salt_cloud_map", os.path.expanduser(salt_cloud_key), "salt_master_add.txt", "ec2-metadata", "salt-master-0.16.4-1.fc18.noarch.rpm"), 
    "salt_cloud_vpc_files": ("cloud_vpc", "cloud_vpc.profiles", "salt_cloud_map", os.path.expanduser(salt_cloud_key), "salt_master_add.txt", "ec2-metadata", "salt-0.17.2.tar.gz", "salt-cloud-0.8.9.tar.gz"), 
    "tags": ("master", "dev", "salt"),
    "DNS_script": "register_master_DNS.py",
    "DNS_command": "r53_register_command.sh",
    "r53_domain": domain,
    "r53_key": route53_key,
    "r53_secret": route53_secret,
    "git_rsa_key": os.path.expanduser(git_rsa_key)
    }

available_profiles = {
                        'aws_master': master_profile.copy(),
                            }
