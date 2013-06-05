# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from seed.profiles.aws import available_profiles as AWS_PROFILES
from seed.profiles.utils import Struct

SEED_PROFILES = {}
SEED_PROFILES.update(AWS_PROFILES)
[SEED_PROFILES.update({
    key: Struct(value)})
        for key, value in SEED_PROFILES.items()]

available_profiles = {}
[available_profiles.update({
    name.upper():profile}) for name, profile in SEED_PROFILES.items()]
available_profiles = Struct(available_profiles)

def get_profile(profile_name, overwrite={}):
    # Oh, the beauty of working with dicts....
    profile = SEED_PROFILES.copy().get(profile_name, Struct({}))
    for attr in overwrite.keys():
        profile[attr] = overwrite.get(key)
    
    return profile 
    