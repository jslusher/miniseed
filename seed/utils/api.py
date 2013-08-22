# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from seed import settings
from seed.exceptions import \
    SeedDriverNotSupportedError, SeedImageNotAvailableError
from seed.utils.keys import run_local_command

from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver

import os
import logging
logger = logging.getLogger(__name__)

_supported_drivers = {
    'aws': Provider.EC2
}

def find_script(file_name):
    return os.path.abspath(os.path.join(settings.RESOURCE_PATH, 
        file_name))

def obtain_driver(seed_profile):
    """
    @param: seed_profile[seed.profiles.profile]

    raises:
        SeedDriverNotSupportedError

    returns:
        libcloud.compute.type.Provider
    """
    if seed_profile.driver not in _supported_drivers.keys():
        raise SeedDriverNotSupportedError("%s [%s]" 
            % (seed_profile.driver, _supported_drivers.keys()))

    driver = get_driver(_supported_drivers.get('aws'))
    logger.debug("Using %s driver. [profile: %s] " %( seed_profile.driver, seed_profile))
    return driver(settings.AWS_ACCESS, settings.AWS_SECRET)

def define_image(seed_profile, libcloud_driver):
    """
    @param: seed_profile[seed.profiles.profile]
    @param: libcloud_driver[libcloud.compute.base.NodeDriver]
        
    raises:
        SeedImageNotAvailableError

    returns:
        <str>, <str>
    """
    try:
        image = libcloud_driver.list_images(
            ex_image_ids=[seed_profile.ami])[0]
        return image.id, image.name
    except IndexError:
        raise SeedImageNotAvailableError

def obtain_image(seed_profile, libcloud_driver):
    """
    @param: seed_profile[seed.profiles.profile]
    @param: libcloud_driver[libcloud.compute.base.NodeDriver]
    
    raises:
        SeedImageNotAvailableError

    returns:
        libcloud.compute.base.NodeImage
    """
    try:
        return libcloud_driver.list_images(
            ex_image_ids=[seed_profile.ami])[0]
    except IndexError:
        raise SeedImageNotAvailableError

def obtain_instances(instance_uuids, libcloud_driver):
    """
    @param: libcloud_driver[libcloud.compute.base.NodeDriver
    @param: instance_uuids[list<str>]

    returns:
        [ libcloud.compute.base.NodeImage, ]
    """
    return libcloud_driver.list_nodes(instance_uuids)
