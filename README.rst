MiniSeed
########

Taken from Leechseed and stripped down for use with salt-cloud. Intended to
launch a salt-master equipped with everything salt-cloud needs to deploy the
rest of the environment.

Deployment Examples
-------------------

Setting the environment variables in your keys.sh file will give miniseed what
it needs to authenticate to AWS and launch your environment.

So you want to share your dev keys?
***********************************

.. code-block:: bash

    $ python -m seed -a package-deploy-keys -p aws_master -x /path/to/place/export

Keys.sh
*******

    You're going to need these items to deploy the salt-cloud master:

.. code-block:: bash

 AWS_ACCESS_KEY_ID=''
 AWS_SECRET_ACCESS_KEY=''
 BITBUCKET_ID=''
 BITBUCKET_PASSWORD=''
 ROUTE53_KEY=''
 ROUTE53_SECRET=''
 R53_MIN_KEY=''
 R53_MIN_SECRET=''
 SALT_CLOUD_KEY=''
 GIT_PKEY=''

 DNS_DOMAIN='dev.next.opinionlab.com'

 export AWS_ACCESS_KEY_ID
 export AWS_SECRET_ACCESS_KEY
 export ROUTE53_KEY
 export ROUTE53_SECRET
 export SALT_CLOUD_KEY
 export GIT_PKEY
 export BITBUCKET_ID
 export BITBUCKET_PASSWORD
 export DNS_DOMAIN

 # Fedora
 #export SSL_CERT_FILE=/etc/pki/tls/certs/ca-bundle.crt

 #OSX: run the bash script found here to install the ca-bundle:
 #https://gist.github.com/1stvamp/2158128
 #export SSL_CERT_FILE=/usr/share/curl/ca-bundle.crt

Launch a salt-master 
********************
    With your map_file, cloud, and cloud.profile configured for you deployment,
    run the following:
.. code-block:: bash
    $ pip install -r requirements.txt
    $ source "/path/to/keys.sh"
    $ python -m seed -a launch -p aws_master -n 'name-of-salt-cloud-master'

Remove a domain from an instance
********************************
.. code-block:: bash

    $ export DNS_DOMAIN="dev.next.opinionlab.com"
    $ python -m seed -a remove-domain --provider aws -n bulbasaur
