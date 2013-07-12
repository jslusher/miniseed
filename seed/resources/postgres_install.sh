#!/usr/bin/env bash

sudo yum -y install postgresql postgresql-devel

sudo postgresql-setup initdb
sudo systemctl start postgresql.service
sudo systemctl enable postgresql.service
