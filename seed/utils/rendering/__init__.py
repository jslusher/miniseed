# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import random
from seed import settings

def generate_password():
    # TODO: Build a real random password generator
    chars = """aoeuidhtnspyfgcrlqjkxbmwvz1234567890AOEUIDHTNSPYFGCRLQJKXBMWVZ!@#$%^&*"""
    return ''.join([chars[random.randint(0,len(chars)-1)] for index in range(64)])

def generate_deploy_keys_bootstrap_script():
    script_path = '/tmp/bootstrap_deploy_keys.sh'

    with open(script_path, 'wb+') as stream:
        stream.write("""#!/usr/bin/env bash
source /usr/bin/virtualenvwrapper.sh
mkvirtualenv bulbasaur -p $(which python2.7)
workon bulbasaur
pip install requests==1.2.0

# Now we can run python scripts automagicly
echo "workon bulbasaur" >> ~/.bashrc

exit 0
""")

    return script_path

def generate_source_keyfile(script_path=None, **kwargs):
    script_path = script_path or '/tmp/source_keys.sh'

    values = {
        "aws_access_key_id": settings.AWS_ACCESS,
        "aws_secret_access_key": settings.AWS_SECRET,
        "bitbucket_id": settings.BITBUCKET_ID,
        "bitbucket_password": settings.BITBUCKET_PASSWORD,
        
        "env_profile": "development", # This is an informative flag that'll tell you which bash-keys-file you're using. 
        "db_host": '',
        "db_port": '',
        "db_password": generate_password(),
        "db_username": 'pokeball',
        "db_name": "bulbasaur_vinewhip",

        "unix_user": "ec2-user",
        "unix_group": "www-data",

        "dns_namespace": settings.DNS_DEFAULT,
        "dns_server_namespace": '.'.join([settings.name, settings.DNS_DEFAULT]),
        "server_name": settings.name,
    }
    values.update(kwargs)
    with open(script_path, 'wb+') as stream:
        stream.write("""#!/usr/bin/env bash

AWS_ACCESS_KEY_ID='%(aws_access_key_id)s'
AWS_SECRET_ACCESS_KEY='%(aws_secret_access_key)s'
BITBUCKET_ID='%(bitbucket_id)s'
BITBUCKET_PASSWORD='%(bitbucket_password)s'

BULBASAUR_PROFILE="%(env_profile)s"
BULBASAUR_DB_HOST='%(db_host)s'
BULBASAUR_DB_PORT='%(db_port)s'
BULBASAUR_DB_USER='%(db_username)s'
BULBASAUR_DB_PASSWORD='%(db_password)s'
BULBASAUR_VINEWHIP_DB_NAME='%(db_name)s'

BULBASAUR_USER="%(unix_user)s"
BULBASAUR_GROUP="%(unix_group)s"

BULBASAUR_DNS_NAMESPACE="%(dns_namespace)s"
BULBASAUR_DNS_SERVER_NAMESPACE="%(dns_server_namespace)s"
BULBASAUR_SERVER_NAME="%(server_name)s"

export AWS_ACCESS_KEY_ID
export AWS_SECRET_ACCESS_KEY
export BITBUCKET_ID
export BITBUCKET_PASSWORD

export BULBASAUR_PROFILE
export BULBASAUR_DB_HOST
export BULBASAUR_DB_PORT
export BULBASAUR_DB_USER
export BULBASAUR_DB_PASSWORD
export BULBASAUR_VINEWHIP_DB_NAME

export BULBASAUR_USER
export BULBASAUR_GROUP

export BULBASAUR_DNS_NAMESPACE
export BULBASAUR_DNS_SERVER_NAMESPACE
export BULBASAUR_SERVER_NAME

if [[ "$(uname)" == 'Linux' ]];
then
    export SSL_CERT_FILE=/etc/pki/tls/certs/ca-bundle.crt
fi;
if [[ "$(uname)" == 'Darwin' ]];
then
    export SSL_CERT_FILE=/usr/local/opt/curl-ca-bundle/share/ca-bundle.crt
fi;


""" % values)
    
    
    return script_path

def decorate_shell_with_keyfile():
    script_path = '/tmp/decorate_shell.sh'

    with open(script_path, 'wb+') as stream:
        stream.write("""#!/usr/bin/env bash
touch ~/.ssh/config
chmod 644 ~/.ssh/config
sudo echo "Host github.com" >> ~/.ssh/config
sudo echo "    StrictHostKeyChecking no" >> ~/.ssh/config
sudo echo "Host bitbucket.org" >> ~/.ssh/config
sudo echo "    StrictHostKeyChecking no" >> ~/.ssh/config

echo 'if [ -f "/tmp/source_keys.sh" ];then' >> ~/.bashrc
echo '    rm -rf $HOME/keys.sh' >> ~/.bashrc
echo '    mv /tmp/source_keys.sh $HOME/keys.sh' >> ~/.bashrc
echo 'fi;' >> ~/.bashrc
echo 'if [ -f "$HOME/keys.sh" ]; then' >> ~/.bashrc
echo '  chmod 755 $HOME/keys.sh' >> ~/.bashrc
echo '  source $HOME/keys.sh' >> ~/.bashrc
echo '  chmod 400 $HOME/keys.sh' >> ~/.bashrc
echo 'fi;' >> ~/.bashrc

exit 0;
""")
    return script_path
def generate_vinewhip_deployment_keys():
    script_path = '/tmp/register_deployment_keys.py'

    with open(script_path, 'wb+') as stream:
        stream.write("""#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import requests
from requests.auth import HTTPBasicAuth
import sys
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

BITBUCKET_URI = "%(bitbucket_uri)s"
BITBUCKET_ID = os.environ.get('BITBUCKET_ID')
BITBUCKET_PASSWORD = os.environ.get('BITBUCKET_PASSWORD')

auth = HTTPBasicAuth(BITBUCKET_ID, BITBUCKET_PASSWORD)

def get_public_key(public_key_path=None):
    public_key_path = public_key_path or os.path.expanduser("~/.ssh/id_rsa.pub")
    if not os.path.exists(public_key_path):
        return None

    buffer = StringIO.StringIO()
    with open(public_key_path) as stream:
        buffer.write(stream.read())
        buffer.seek(0)

    return buffer


response = requests.post(url=BITBUCKET_URI, 
    data={
        "label": "salt-master-master",
        "key": get_public_key().read().replace('\\n','')
    },
    auth=auth, ) 

sys.stdout.write(str(response.status_code))
sys.stdout.write("\\n")

sys.exit(0) # Signal there wasn't an issue
""" % {
        'bitbucket_uri': settings.BULBASAUR_URI,
        })

    return script_path

def generate_vinewhip_instance():
    script_path = '/tmp/bootstrap_vinewhip.sh'

    with open(script_path, 'wb+') as stream:
        stream.write("""#!/usr/bin/env bash
source /usr/bin/virtualenvwrapper.sh
workon bulbasaur

# http://mail.python.org/pipermail/python-list/2009-October/553277.html
# pip install M2Crypto==0.21.1
# if [ $? == 1 ]; then
#     cd $VIRTUAL_ENV/build/M2Crypto
#     sed s/uname\ \-m/uname\ \-\-hardware-platform/g fedora_setup.sh > fedora-setup-repair.sh
#     chmod 755 ./fedora-setup-repair.sh
#     ./fedora-setup-repair.sh install
#     chmod 444 ./fedora-setup-repair.sh
#     cd $HOME
# else
#     echo "Tis' ok"
# fi;

git clone git@bitbucket.org:importthis/bulbasaur.git
add2virtualenv ~/bulbasaur/leechseed
pip install -r ~/bulbasaur/requirements.txt

# cd ~/bulbasaur/vinewhip && python setup.py install

exit 0
""")

    return script_path

def generate_postgresql_env():
    script_path = "/tmp/bootstrap_postgresql_env.sh"

    with open(script_path, 'wb+') as stream:
        stream.write("""#!/usr/bin/env bash

sudo yum -y install postgresql postgresql-server
sudo touch /var/log/postgresql-server.log
sudo chown postgres.root /var/log/postgresql-server.log
sudo chmod 640 /var/log/postgresql-server.log

# sudo su - postgres
sudo su - postgres -c 'initdb -D /var/lib/pgsql/data'
sudo su - postgres -c 'pg_ctl -D /var/lib/pgsql/data -l /var/log/postgresql-server.log start'

# Give postgres time to startup
sleep 30
sudo su - postgres -c 'createuser -S -R -d %(postgres_db_user)s'
sudo su - postgres -c "echo \\"alter user %(postgres_db_user)s with password '%(postgres_db_user_password)s';\\" |psql"
sudo su - postgres -c "createdb -U %(postgres_db_user)s %(postgres_db_database_name)s"

exit 0

""" % {
    'postgres_db_database_name': os.environ.get('BULBASAUR_VINEWHIP_DB_NAME'),
    'postgres_db_user': os.environ.get('BULBASAUR_DB_USER'),
    'postgres_db_user_password': os.environ.get('BULBASAUR_DB_PASSWORD'),
    'postgres_db_host': os.environ.get('BULBASAUR_DB_HOST', '127.0.0.1'),
    'postgres_db_port': os.environ.get('BULBASAUR_DB_PORT', 5432),
})
    return script_path

def generate_vinewhip_env_standup():
    script_path = "/tmp/standup_vinewhip.sh"

    with open(script_path, 'wb+') as stream:
        stream.write("""#!/usr/bin/env bash
source /usr/bin/virtualenvwrapper.sh
workon bulbasaur

cd $HOME/bulbasaur/vinewhip

chmod 755 manage.py
./manage.py syncdb --noinput
./manage.py migrate --noinput
chmod 440 manage.py

cd $HOME

exit 0
""")
    return script_path

def generate_nginx_env():
    script_path = "/tmp/bootstrap_nginx.sh"

    with open(script_path, 'wb+') as stream:
        stream.write("""#!/usr/bin/env bash
echo "Deploying nginx"
source /usr/bin/virtualenvwrapper.sh
workon bulbasaur

yum -y install nginx supervisor
$HOME/bulbasaur/vinewhip/server_data/bootstrap_permissions.sh
$HOME/bulbasaur/vinewhip/server_data/bootstrap_nginx.sh
$HOME/bulbasaur/vinewhip/server_data/bootstrap_gunicorn.sh
$HOME/bulbasaur/vinewhip/server_data/bootstrap_supervisor.sh
$HOME/bulbasaur/vinewhip/server_data/start_nginx.sh
$HOME/bulbasaur/vinewhip/server_data/run_supervisor.sh


exit 0
""")
    return script_path