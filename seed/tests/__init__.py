import random
import unittest

class TestCaseExample(unittest.TestCase):
    def setUp(self):
        pass

    def test_shuffle(self):
        pass
        #print "test suffle"
    
    def test_failure(self):
        #print "neat failure"

        assert 1 == 2

    def test_error(self):
        #print "neat Error"

        raise Exception("Because, that's why")
