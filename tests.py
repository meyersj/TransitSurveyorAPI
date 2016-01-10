# Copyrigh (C) 2015 Jeffrey Meyers
# This program is released under the "MIT License".
# Please see the file COPYING in the source
# distribution of this software for license terms.

import os
import unittest
import tempfile
import json
from uuid import uuid4

import requests
from flask import Flask

from api import app
from api import db

from api.mod_api.views import verify_user
from api.mod_api.insert import InsertScan, InsertPair, buildGeom

ENDPOINT =  os.getenv("API_ENDPOINT", "127.0.0.1:9000")
INDEX_RESPONSE = "On-Off Index"
API_RESPONSE = "API Module"


class VerifyUserTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def test_VerifyUser_lookup_function(self):
        match, user_id = verify_user("testuser", 1234)
        assert match is not None
        assert user_id is not None

    def test_VerifyUser_endpoint(self):
        rv = self.app.post(
            '/api/verifyUser',
            data=dict(
       	        username="testuser",
		password="1234" 
            ),
            follow_redirects=True
        )
        data = json.loads(rv.data)
        assert "error" not in rv.data
        assert "match" in rv.data
        assert "user_id" in rv.data


class InsertScanTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        uuid = str(uuid4())
        self.on_scan = dict(
            uuid=uuid,
            date="2000-01-01 12:00:00",
            rte="9",
            dir="0",
            lon="-122.5",
            lat="45.5",
            mode="on",
            user_id="testuser"
        )
        self.off_scan = dict(
            uuid=uuid,
            date="2000-01-01 12:30:00",
            rte="9",
            dir="0",
            lon="-122.5",
            lat="45.5",
            mode="off",
            user_id="testuser"
        )

    def test_InsertScan_invalid(self):
        rv = self.app.post(
            '/api/insertScan',
            data=dict(invalidparam="something"),
            follow_redirects=True
        )
        data = json.loads(rv.data)
        assert "error" in data
        assert data["error"] == "invalid input data"
    
    def test_InsertScan_onoff(self):
        insert = InsertScan(**self.on_scan)
        valid, insertID, match = insert.isSuccessful()
        assert valid, "on scan insert failed"
        assert insertID != -1, "on scan insert id should not be -1"
        insert = InsertScan(**self.off_scan)
        valid, insertID, match = insert.isSuccessful()
        assert valid, "off scan insert failed"
        assert insertID != -1, "off scan insert id should not be -1"
        assert match is True, "on-off scans did not get matched"

    def test_InsertScan_onoff_requests(self):
        rv = self.app.post(
            '/api/insertScan',
            data=self.on_scan,
            follow_redirects=True
        )
        data = json.loads(rv.data)
        assert "success" in data and data["success"], "on scan insert request failed"
        rv = self.app.post(
            '/api/insertScan',
            data=self.off_scan,
            follow_redirects=True
        )
        data = json.loads(rv.data)
        assert "success" in data and data["success"], "off scan insert request failed"
        assert "match" in data and data["match"], "matching on-off requests failed"


class InsertPairTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.pair = dict(
            date="2000-01-01 12:00:00",
            rte="193",
            dir="0",
            on_stop="10764",
            off_stop="10770",
            user_id="testuser"
        )

    def test_InsertPair_invalid_params(self):
        rv = self.app.post(
            '/api/insertPair',
            data=dict(invalidparam="something"),
            follow_redirects=True
        )
        data = json.loads(rv.data)
        assert "error" in data
        assert data["error"] == "invalid input data"
   
    def test_InsertPair_basic(self):
        insert = InsertPair(**self.pair)
        valid, insertID = insert.isSuccessful()
        assert valid, "InsertPair returned invalid response"
        assert insertID != -1, "InsertPair insert id should not be -1"


class StopLookupTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def test_build_geom(self):
        success, geom = buildGeom(45.5, -122)
        assert success, "failed to build geometry"

    def test_stopLookup_request(self):
        rv = self.app.post(
            '/api/stopLookup',
            data=dict(
                lat="45.5",
                lon="-122.5",
                rte="9",
                dir="0"
            ),
            follow_redirects=True
        )
        assert rv.status_code == 200
        data = json.loads(rv.data)
        assert not data["error"], "stop lookup returned error"
        assert data["stop_name"], "stop name is missing"


class IndexTest(unittest.TestCase):
    
    def setUp(self):
        self.app = app.test_client()

    def test_index(self):
        rv = self.app.get('/', follow_redirects=True)
        assert rv.status_code == 200
        assert rv.data == INDEX_RESPONSE
    
    def test_api_index(self):
        rv = self.app.get('/api', follow_redirects=True)
        assert rv.status_code == 200
        assert rv.data == API_RESPONSE


if __name__ == '__main__':
    unittest.main()
