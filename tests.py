# Copyright © 2015 Jeffrey Meyers
# This program is released under the "MIT License".
# Please see the file COPYING in the source
# distribution of this software for license terms.

import os
import unittest
import tempfile
import json

import requests
from flask import Flask

from api import app
from api import db

from api.mod_api.models import OnTemp


ENDPOINT =  os.getenv("API_ENDPOINT", "default_ip_address")
INDEX_RESPONSE = "On-Off Index"
API_RESPONSE = "API Module"


class APITestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def tearDown(self):
        pass

    def test_index_endpoint(self):
        rv = self.app.get('/')
        assert rv.data == INDEX_RESPONSE
    
    def test_mod_api_endpoint(self):
        rv = self.app.get('/api/')
        assert rv.data == API_RESPONSE

    #def test_verify_user(self):
    #    rv = self.app.post('/api/verifyUser', data=dict(
    #            credentials="{\"username\":\"testuser\", \"password\":\"1234\"}" 
    #    ), follow_redirects=True)
    #    res = json.loads(rv.data)

class ServerUp(unittest.TestCase):
    
    #def setUp(self):
    #    pass 

    #def tearDown(self):
    #    pass

    def test_production_index(self):
        r = requests.get("http://"+ENDPOINT)
        assert r.status_code == 200
        assert r.text == INDEX_RESPONSE

    def test_production_mod_api(self):
        r = requests.get("http://"+ os.path.join(ENDPOINT, "api"))
        assert r.status_code == 200
        assert r.text == API_RESPONSE

if __name__ == '__main__':
    unittest.main()
