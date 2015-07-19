import os
import unittest
import tempfile

from api import app

class APITestCase(unittest.TestCase):

    def setUp(self):
	# something before each test
        pass        

    def tearDown(self):
        # something after each test
        pass

    def test_blank(self):
        assert 1 == 1

if __name__ == '__main__':
    unittest.main()
