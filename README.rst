LeechSeed
#########

Seed it and it'll grow and drain your resources until you stop it.

Leechseed is the control-point you use to configure vinewhip. 

Deployment Examples
-------------------

    The following will build out 9 instances. You can do verious testing on said instances. 

    You'll have to obtain the Public IPs for the aws console. 


So you want to share your dev keys?
***********************************

.. code-block:: bash

    $ python -m seed -a package-deploy-keys -p aws_master -x /path/to/place/export
    $ python -m seed -a install-deploy-keys -p aws_minion -k /path/of/archive/to/install


Keys.sh
*******

    You're going to need this to buildout vinewhip. 

.. code-block:: bash

    #!/usr/bin/env bash

    AWS_ACCESS_KEY_ID='an aws id'
    AWS_SECRET_ACCESS_KEY='an aws secret'
    BITBUCKET_ID='a bitbucket username'
    BITBUCKET_PASSWORD='a bitbucket password'

    BULBASAUR_DB_HOST=''
    BULBASAUR_DB_PORT=''
    BULBASAUR_DB_USER='pokeball'
    BULBASAUR_DB_PASSWORD='not_used_yet'
    BULBASAUR_VINEWHIP_DB_NAME='bulbasaur_vinewhip'

    export AWS_ACCESS_KEY_ID
    export AWS_SECRET_ACCESS_KEY
    export BITBUCKET_ID
    export BITBUCKET_PASSWORD

    export BULBASAUR_DB_HOST
    export BULBASAUR_DB_PORT
    export BULBASAUR_DB_USER
    export BULBASAUR_DB_PASSWORD
    export BULBASAUR_VINEWHIP_DB_NAME

    # http://libcloud.apache.org/docs/ssl-certificate-validation.html
    # osx
    export SSL_CERT_FILE=/usr/local/opt/curl-ca-bundle/share/ca-bundle.crt
    # Fedora
    export SSL_CERT_FILE=/etc/pki/tls/certs/ca-bundle.crt

Setup Vinewhip, the Bulbasaur API
*********************************

.. code-block:: bash

    $ python -m seed -a launch -n bulbasaur -p aws_master && python -m seed -a empower -n bulbasaur & python -m seed -a register-domain -n bulbasaur --provider aws

M2Crypto Fix
************

.. code-block:: bash

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


Launch a master with a domain
*****************************

.. code-block:: bash
    
    $ export BULBASAUR_DNS_DEFALUT="dev.next.opinionlab.com"
    $ python -m seed -a launch -p aws_master -n bulbasaur && python -m seed -a register-domain --provider aws -n bulbasaur & python -m seed -a empower -n bulbasaur

Remove a domain from an instance
********************************

    $ export BULBASAUR_DNS_DEFALUT="dev.next.opinionlab.com"
    $ python -m seed -a remove-domain --provider aws -n bulbasaur
    
Launch a master
***************

.. code-block:: bash

    $ pip mkvirtualenv -p $(which python2.7)
    $ pip install M2Crypto==0.21.1 # http://mail.python.org/pipermail/python-list/2009-October/553277.html
    $ cd ~/bulbasaur && pip install -r requirments.txt
    $ add2virtalenv ~/bulbasaur/leechseed
    $ cd ~/bulbasaur/leechseed && python -m seed -a launch -p aws_master -n master0 && python -m seed -a empower -n master0 &


Launch a cluster
****************

.. code-block:: bash
    
    # Not advisable as you cannot cancel these jobs
    for i in {1..3}; do (cd ~/workspace/opinionlab/bulbasaur/leechseed && python -m seed -a launch -p aws_master -n delta$i && python -m seed -a empower -n delta$i &); done

    python -m seed -a launch -p aws_master -n alpha3 &


TODO
----

* Standup Vinewhip, the last step. 
* Tie in Sentry

