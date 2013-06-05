# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from seed.exceptions import SSHKeyDoesNotExist

def deploy_key(public_key=None):
    """
    None returns the ~/.ssh/id_rsa
    """
    import requests
    from requests.auth import HTTPBasicAuth
    import json
    import StringIO

    bitbucket_url = "https://api.bitbucket.org/1.0/repositories/importthis/bulbasaur/deploy-keys/"
    bitbucket_payload = json.dumps({'label': 'bulbasaur-deploy-%s' % env_name,
                                    'key': public_key})
    auth = HTTPBasicAuth(os.environ['BITBUCKET_ID'],
                         os.environ['BITBUCKET_PASSWORD'])
    headers = {'content-type': 'application/json'}
    params = {'format': 'json'}
    response = requests.post(bitbucket_url, data=bitbucket_payload,
                             verify=True, auth=auth,
                             params=params, headers=headers)
    logger.debug("updating bulbasaur deploy keys")
    if response.status_code != 200:
        logger.debug(response.text)
        raise Exception("Bitbucket deploy key creation was not successful")
    logger.debug("bulbasaur deploy keys successfully updated!")

def create_ssh_key_for_bitbucket(env_name):
    """
    Creates an SSH key, deploys it to bitbucket for bulbasaur, then returns
    the private key.
    """
    import requests
    from requests.auth import HTTPBasicAuth
    import json
    import StringIO

    from paramiko.rsakey import RSAKey

    logger.debug("generating RSA keypair")
    private_key = RSAKey.generate(4096)
    private_key_file = StringIO.StringIO()
    private_key.write_private_key(private_key_file)
    private_key_file.seek(0)
    public_key = RSAKey.from_private_key(private_key_file)
    public_key_str = "%s %s" % (public_key.get_name(), public_key.get_base64())
    # rewind the private_key_file
    private_key_file.seek(0)
    logger.debug("successfully generated RSA keypair")

    bitbucket_url = "https://api.bitbucket.org/1.0/repositories/importthis/bulbasaur/deploy-keys/"
    bitbucket_payload = json.dumps({'label': 'bulbasaur-deploy-%s' % env_name,
                                    'key': public_key_str})
    auth = HTTPBasicAuth(os.environ['BITBUCKET_ID'],
                         os.environ['BITBUCKET_PASSWORD'])
    headers = {'content-type': 'application/json'}
    params = {'format': 'json'}
    response = requests.post(bitbucket_url, data=bitbucket_payload,
                             verify=True, auth=auth,
                             params=params, headers=headers)
    logger.debug("updating bulbasaur deploy keys")
    if response.status_code != 200:
        logger.debug(response.text)
        raise Exception("Bitbucket deploy key creation was not successful")
    logger.debug("bulbasaur deploy keys successfully updated!")
    return private_key_file
