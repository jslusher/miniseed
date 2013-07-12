#!/usr/bin/env python 
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import json
import requests
from requests.auth import HTTPBasicAuth

BITBUCKET_ID = os.environ.get('BITBUCKET_ID')
BITBUCKET_PASSWORD = os.environ.get('BITBUCKET_PASSWORD')
auth = HTTPBasicAuth(BITBUCKET_ID, BITBUCKET_PASSWORD)


response = requests.get('https://api.bitbucket.org/1.0/repositories/importthis/bulbasaur/deploy-keys/', auth=auth)

content = json.loads(response.content)

for item in content:
    print "Removing...", item.get('pk')
    response = requests.delete('https://api.bitbucket.org/1.0/repositories/importthis/bulbasaur/deploy-keys/%d' %item.get('pk'), auth=auth, data={'pk':item.get('pk')})


