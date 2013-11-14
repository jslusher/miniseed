# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from seed.profiles import aws

class NameDict(object):
    def __init__(self, name_dict):
        return self.__dict__.update(name_dict)

def get_profile(pname):
    profile_name = getattr(aws, pname)
    profile = NameDict(profile_name)
    return profile