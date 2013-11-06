# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from argparse import Namespace
import os
import sys
import logging
from seed.base import validate_settings, define_arguments

AWS_ACCESS = os.environ.get('AWS_ACCESS_KEY_ID', None)
AWS_SECRET = os.environ.get('AWS_SECRET_ACCESS_KEY', None)
ROUTE53_KEY = os.environ.get('ROUTE53_KEY', None)
ROUTE53_SECRET = os.environ.get('ROUTE53_SECRET', None)
GIT_PKEY = os.environ.get('GIT_PKEY', None)
SALT_CLOUD_KEY = os.environ.get('SALT_CLOUD_KEY', None)

logger = logging.getLogger(__name__)


def build_logger(name=None):
    debug_log_file = "/tmp/seeder_%s.log" % name or 'None'
    logging.basicConfig(level=logging.DEBUG,
        filemode="w",
        filename=debug_log_file, )

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console_formatter = logging.Formatter("%(name)-20s: %(levelname)-8s %(message)s")
    console.setFormatter(console_formatter)
    logging.getLogger('').addHandler(console)
    print "debug_log: %s" % debug_log_file

settings = define_arguments()
setattr(settings, 'DEBUG', True)
setattr(settings, 'AWS_ACCESS', AWS_ACCESS)
setattr(settings, 'AWS_SECRET', AWS_SECRET)
setattr(settings, 'ROUTE53_KEY', ROUTE53_KEY)
setattr(settings, 'ROUTE53_SECRET', ROUTE53_SECRET)
setattr(settings, 'GIT_PKEY', GIT_PKEY)
setattr(settings, 'SALT_CLOUD_KEY', SALT_CLOUD_KEY)
setattr(settings, 'BITBUCKET_ID', os.environ.get("BITBUCKET_ID", None))
setattr(settings, 'BITBUCKET_PASSWORD', os.environ.get("BITBUCKET_PASSWORD", None))
setattr(settings, 'BULBASAUR_URI', 'https://api.bitbucket.org/1.0/repositories/importthis/bulbasaur/deploy-keys/')
setattr(settings, 'SEED_PATH', os.path.abspath(os.path.dirname(__file__)))
setattr(settings, "RESOURCE_PATH", os.path.join(os.path.abspath(os.path.dirname(__file__)), "resources"))
setattr(settings, "NETWORK_DELAY", 5)
setattr(settings, "NETWORK_TIMEOUT", 540) # 9 min
setattr(settings, "SSH_PORT", 22)
setattr(settings, "DNS_DEFAULT", os.environ.get("DNS_DOMAIN", None))
validate_settings(settings)
build_logger(settings.name)
