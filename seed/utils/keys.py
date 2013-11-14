import getpass
import logging
import os
import socket
from paramiko import RSAKey
from libcloud.compute.deployment import SSHKeyDeployment, \
    MultiStepDeployment, FileDeployment

try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

logger = logging.getLogger(__name__)

def generate_salt_key_for_minion(minion_hostname):
    """
    Install key in pki and return FileDeployment
    """
    command = "cd /tmp/ && salt-key --gen-keys=%s" % minion_hostname
    run_local_command(command)
    pem_key = FileDeployment("/tmp/%s.pem" % minion_hostname, 
        target="/etc/salt/pki/minion/%s.pem" % minion_hostname)
    public_key = FileDeployment("/tmp/%s.pub" % minion_hostname,
        target="/etc/salt/pki/minion/%s.pub" % minion_hostname)

    return (pem_key, public_key)

def get_public_key(public_key_path=None):
    public_key_path = public_key_path or os.path.expanduser("~/.ssh/id_rsa.pub")
    if not os.path.exists(public_key_path):
        logger.error("File dose not exist. %s" % public_key_path)
        return None

    buffer = StringIO.StringIO()
    with open(public_key_path) as stream:
        buffer.write(stream.read())
        buffer.seek(0)

    return buffer

def get_public_key_from_file(public_key_path=None):
    public_key_path = public_key_path or os.path.expanduser("~/.ssh/id_rsa.pub")
    print "public_key_path: %s" % public_key_path
    if not os.path.exists(public_key_path):
        logger.error("File does not exist. %s" % public_key_path)
        return None

    ssh_key_deployment = None
    with open(public_key_path) as stream:
        ssh_key_deployment = SSHKeyDeployment(stream.read())
    return ssh_key_deployment

def generate_keypair(private_key_path, public_key_path, bits=8192, overwrite=False):
    if not os.path.exists(os.path.dirname(private_key_path)):
        os.makedirs(os.path.dirname(private_key_path))

    if not os.path.exists(private_key_path) or overwrite:
        logger.debug("Creating keypair here %s" % private_key_path)
        key = RSAKey.generate(bits=bits,)
        with open("%s" % public_key_path, 'wb+') as stream:
            stream.write("ssh-rsa ")
            stream.write(key.get_base64())
            stream.write(" %s@%s" % (getpass.getuser(), socket.gethostname()))
        with open("%s" % private_key_path, 'wb+') as stream:
            key.write_private_key(stream)

        os.chmod("%s" % private_key_path, 0600)
        os.chmod("%s" % public_key_path, 0644)
        key = None
    else:
        logger.debug("Keypair exists %s" % private_key_path)

    return private_key_path, public_key_path

def run_local_command(command, *args):
    arguments = [cmd]
    arguments.extend(args)
    # Because Popen rather ['a b c d e'] rather then [a,b,c,d,e]
    arguments = [' '.join(arguments)]
    logger.debug("Running local command: %s" % arguments)
    proc = subprocess.Popen(arguments, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, shell=True)

    while proc.poll() is None:
        continue

    logger.debug(proc.stdout.read())
    logger.error(proc.stderr.read())
    