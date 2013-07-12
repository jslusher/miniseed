#!/bin/bash
#Requirements
# - you've run bootstrap_python_env.sh
# - you've run postgres_install.sh
# - port 8080 has been opened by the salt-master

cd $HOME/
mkvirtualenv django-env
workon django-env
sudo pip install django
sudo mkdir /srv/django
cd /srv/django
sudo $HOME/.virtualenvs/django-env/bin/django-admin.py startproject test_site

#test_site/settings.py
