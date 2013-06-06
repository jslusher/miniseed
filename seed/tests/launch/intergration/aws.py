import unittest

from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver as get_node_driver
import os
AWS_ACCESS = os.environ.get("AWS_ACCESS_KEY_ID", "")
AWS_SECRET = os.environ.get("AWS_SECRET_ACCESS_KEY", "")

class TestAMIAvailability(unittest.TestCase):
    def test_current_aws_creds_work(self):
        from seed.profiles.aws.constants import i386
        node_driver = get_node_driver(Provider.EC2)(AWS_ACCESS, AWS_SECRET)
        node_driver.list_nodes()

    def test_current_aws_ami_exists(self):
        from seed.profiles.aws.constants import i386
        node_driver = get_node_driver(Provider.EC2)(AWS_ACCESS, AWS_SECRET)
        assert node_driver.list_images(ex_image_ids=[i386.ami])

        
