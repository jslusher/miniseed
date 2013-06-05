# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re
class ValidationError(Exception):
    pass

def validate_node_name(name, regex='^([a-z0-9A-Z\-])+$'):
    if name.find('$') > -1:
        raise ValidationError("%s is not a proper name. [ %s ]" 
            % (name, regex))

    name_matcher = re.compile(regex)
    match = name_matcher.match(name)
    if match is None:
        raise ValidationError("%s is not a proper name. [ %s ]" 
            % (name, regex))

def validate_aws(profile):
    # If failed, raise AttributeError
    return True

def validate_rackspace(profile):
    # If failed, raise AttributeError
    return True
