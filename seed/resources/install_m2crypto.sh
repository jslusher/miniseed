#!/usr/bin/env bash

# http://mail.python.org/pipermail/python-list/2009-October/553277.html
pip install M2Crypto
if [ $? == 1 ]; then
    cd $VIRTUAL_ENV/build/M2Crypto
    sed s/uname\ \-m/uname\ \-\-hardware-platform/g fedora_setup.sh > fedora-setup-repair.sh
    chmod 755 ./fedora-setup-repair.sh
    ./fedora-setup-repair.sh install
    chmod 444 ./fedora-setup-repair.sh
    cd $HOME
else
    echo "Tis' ok"
fi;