#!/usr/bin/env bash

sudo yum -y install which
sudo yum -y install python-virtualenv python-virtualenvwrapper

mkdir -p $HOME/.virtualenvs
source /usr/bin/virtualenvwrapper.sh
# Doing this allows me to invoke python scripts just as easily. 
touch ~/.bashrc
echo "source /usr/bin/virtualenvwrapper.sh" >> ~/.bashrc