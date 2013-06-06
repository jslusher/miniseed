# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import unittest
from seed.profiles import available_profiles, SEED_PROFILES, get_profile

class TestProfilesUtils(unittest.TestCase):
    def setUp(self):
        self.profile_names = ['aws_master', 'aws_minion']

    def tearDown(self):
        self.profile_names = None

    def test_SEED_PROFILES(self):
        for name in self.profile_names:
            assert name in SEED_PROFILES.keys()

    def test_get_profile(self):
        for profile_name in self.profile_names:
            assert SEED_PROFILES.get(profile_name) == get_profile(profile_name)


class TestProfiles(unittest.TestCase):
    def test_aws_profile(self):
        pass
    
    def test_aws_master_profile(self):
        salt_master = available_profiles.AWS_MASTER.copy()
        required_keys = ['driver', 'ami', 'ami_user', 'ami_group']
        for key in required_keys:
            assert key in salt_master.keys()
    
    def test_aws_minion_profile(self):
        salt_minion = available_profiles.AWS_MINION.copy()
        required_keys = ['driver', 'ami', 'ami_user', 'ami_group']
        for key in required_keys:
            assert key in salt_minion.keys()

