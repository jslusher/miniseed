#parses arguments, tests them, applies them to settings

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import argparse
import os
import sys

from unittest import TestLoader, TestResult, TextTestRunner
import logging
logger = logging.getLogger(__name__)
AWS_ACCESS = os.environ.get('AWS_ACCESS_KEY_ID', None)
AWS_SECRET = os.environ.get('AWS_SECRET_ACCESS_KEY', None)

def define_arguments():
    parser = argparse.ArgumentParser(description="""
        Launch a salt master instance with me. 
        Any value not specified will prompt the user.""", )
    
    # Interactive
    parser.add_argument('-g', '--generate-profile',
        dest="profile_generate", default=None, type=unicode,
        help="Would you like to generate a AWS, Rackspace, or other profile?", )
    
    parser.add_argument('-f', '--force',
        dest="force", action="store_true", 
        help="Tells seed to ignore the error that is raised by not having aws creds",)

    parser.add_argument('-a', '--action',
        dest="action", default='list', type=unicode,
        help="View currently deployed nodes", )

    parser.add_argument('-p', '--profile', 
        dest="operation_profile", default=None, type=unicode,
        help="You can specify a profile to launch with in json format",)

    parser.add_argument('-l', '--list-profiles',
        dest="operation_profile_list", default=False,
        action="store_true", help="List profiles that are installed", )

    parser.add_argument('-n', '--name',
        dest="name", default=None, type=unicode,
        help="Names must be unique", )

    parser.add_argument('-d', '--domain',
        dest="domain", default=None, type=unicode,
        help="Domain name you would like to apply to an instance", )
    parser.add_argument('-e', '--provider',
        dest="provider", default=None, type=unicode,
        help="Rather then passing a profile to get a driver, you just need a provider.", )
    parser.add_argument('-x', '--export-key-archive-path',
        dest="key_export_path", default=None, type=unicode,
        help="Path to export key files to /key/path", )
    parser.add_argument('-k', '--import-key-archive-path',
        dest="key_import_path", default=None, type=unicode,
        help="Import an archive from a /key/path", )
    parser.add_argument('-o', '--output',
        dest="output_path", default=None, type=unicode,
        help="Where to place this output data",)
    parser.add_argument('-m', '--minion-names',
        dest="minion_names", default=None, type=unicode,
        help="The minions that will attach to a master instance", )
    parser.add_argument('-t', '--template-path', 
        dest="template_path", default=None, type=unicode,
        help="Path to the jinja2 templates", )
    parser.add_argument('-s', '--run-tests',
        dest="run_tests", action="store_true", default=False, )
    parser.add_argument('-c', '--drain-c',
        dest="drain_c", action="store_true", 
        help="For some reason -c is being passed. So, we'll just sink it.", )
   
    settings = parser.parse_args(sys.argv) 
    if settings.run_tests:
        run_tests(settings)
        logger.info("All tests completed.")
        sys.exit(0)

    return settings

def validate_settings(settings):
    for attribute in ["SEED_PATH", "RESOURCE_PATH", "NETWORK_DELAY", "NETWORK_TIMEOUT", "SSH_PORT"]:
        if not attribute in settings.__dict__.keys():
            raise ValueError("Missing Attribute: [%s]" % attribute)
     
    if settings.AWS_ACCESS is None or settings.AWS_SECRET is None:
        if not settings.force:
            #raise ValueError("You must supply some amazon keys to launch a salt-master instance.")
            pass

    if settings.template_path is None:
        settings.template_path = os.path.abspath(os.path.dirname(__file__))

def run_tests(settings):
    test_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'tests')
    try:
        test_suite = TestLoader().discover(start_dir=test_path, pattern="*.py", top_level_dir=None)
    except TypeError, e:
        raise TypeError("A unit test has bad grammer. \n %s" %e)
    
    test_runner = TextTestRunner(stream=sys.stderr, descriptions=True, verbosity=1)
    test_runner.run(test_suite)
    sys.exit(0)

