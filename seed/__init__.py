# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from argparse import Namespace
import os
import sys
from django.core.exceptions import ImproperlyConfigured
from seed.base import validate_settings

import logging
logger = logging.getLogger(__name__)
    
try:
    from django.conf import settings as django_settings
    settings = Namespace()
    setattr(settings, "AWS_ACCESS", django_settings.AWS_ACCESS)
    setattr(settings, "AWS_SECRET", django_settings.AWS_SECRET)
    setattr(settings, 'SEED_PATH', 
        getattr(django_settings, "SEED_PATH", 
            os.path.abspath(os.path.dirname(__file__))))
    setattr(settings, "RESOURCE_PATH", 
        getattr(django_settings, "RESOURCE_PATH",
            os.path.join(os.path.abspath(os.path.dirname(__file__)), "resources")))
    setattr(settings, "NETWORK_DELAY",
        getattr(django_settings, "NETWORK_DELAY", 5))
    setattr(settings, "NETWORK_TIMEOUT",
        getattr(django_settings, "NETWORK_TIMEOUT", 540)) # 9min
    setattr(settings, "SSH_PORT", 
        getattr(django_settings, "SSH_PORT", 22))
    setattr(settings, "BITBUCKET_ID", 
        getattr(django_settings, "BITBUCKET_ID", os.environ.get("BITBUCKET_ID", None)))
    setattr(settings, "BITBUCKET_PASSWORD", 
        getattr(django_settings, "BITBUCKET_PASSWORD", os.environ.get("BITBUCKET_PASSWORD", None)))
    setattr(settings, "BULBASAUR_URI",
        getattr(django_settings, "BULBASAUR_URI", "https://api.bitbucket.org/1.0/repositories/importthis/bulbasaur/deploy-keys/"))
    setattr(settings, "DNS_DEFAULT",
        getattr(django_settings, "BULBASAUR_DNS_DEFAULT", "dev.next.opinionlab.com."))

    validate_settings(settings)
    logger.debug("Django env activated")

except ImproperlyConfigured:
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
        logger.info("Debug log is located here %s" % debug_log_file)
    
        logger.debug("Django env not detected, falling back to settings. ")

    from seed.base import \
        define_arguments, AWS_ACCESS, AWS_SECRET

    settings = define_arguments()
    setattr(settings, 'DEBUG', True)
    setattr(settings, 'AWS_ACCESS', AWS_ACCESS)
    setattr(settings, 'AWS_SECRET', AWS_SECRET)
    setattr(settings, 'BITBUCKET_ID', os.environ.get("BITBUCKET_ID", None))
    setattr(settings, 'BITBUCKET_PASSWORD', os.environ.get("BITBUCKET_PASSWORD", None))
    setattr(settings, 'BULBASAUR_URI', 'https://api.bitbucket.org/1.0/repositories/importthis/bulbasaur/deploy-keys/')
    setattr(settings, 'SEED_PATH', 
        os.path.abspath(os.path.dirname(__file__)))
    setattr(settings, "RESOURCE_PATH", 
        os.path.join(os.path.abspath(os.path.dirname(__file__)), "resources"))
    setattr(settings, "NETWORK_DELAY", 5)
    setattr(settings, "NETWORK_TIMEOUT", 540) # 9 min
    setattr(settings, "SSH_PORT", 22)
    setattr(settings, "DNS_DEFAULT", os.environ.get("BULBASAUR_DNS_NAMESPACE", None))
    validate_settings(settings)
    build_logger(settings.name)

