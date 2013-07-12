# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import subprocess
from subprocess import CalledProcessError

user = 'jslusher'
password = 'th3Butch3r#6'


cmd = "psql -c "create user %s with password '%s'"" % (user, password)
#cuser = """psql -c \"create user %s with password '%s'\""" % (user, password)
cuser = [ 'psql', '-c', cmd ] % (user, password)

try:
    create_user = subprocess.Popen(cuser, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

except CalledProcessError as e:
    print e
    pass

print cuser
