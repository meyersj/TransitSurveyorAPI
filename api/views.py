from flask import request
from flask import jsonify
from api import app, db
from insert import InsertScan, InsertPair
from models import Users
import datetime
import json
import logging
import hashlib

CREDENTIALS = "credentials"
USERNAME = "username"
PASSWORD = "password"
KEYS = "keys"
DATA = "data"
UUID = "uuid"
DATE = "date"
LINE = "rte"
DIR = "dir"
LON = "lon"
LAT = "lat"
MODE = "mode"
ON_STOP = "on_stop"
OFF_STOP = "off_stop"
USER = "user_id"
SALT = "SALT"
TESTUSER = "testuser"

@app.route('/')
def index():
    return "Testing"

def verify_user(username, password):
    user_match = False
    password_match = False
    user_id = -1
    user = Users.query.filter_by(username=username).first()
   
    if user:
        user_match = True
        password_hash = hashlib.sha256(password + app.config[SALT]).hexdigest()
        if password_hash == user.password_hash:
            password_match = True
            user_id = user.username
    else:
        app.logger.warn("user name " + str(username) + " did not match") 

    return user_match, password_match, user_id


@app.route('/verifyUser', methods=['POST'])
def verifyUser():
    cred = json.loads(request.form[CREDENTIALS])
    username = cred[USERNAME]
    password = cred[PASSWORD]
    user_match, password_match,user_id = verify_user(username, password)  
    return jsonify(user_match=user_match, password_match=password_match, user_id=user_id)


#api route for on off locations from scanner
@app.route('/insertScan', methods=['POST'])
def insertScan():
    data = json.loads(request.form[DATA])
    valid = False
    insertID = -1
    uuid = data[UUID]
    date = datetime.datetime.strptime(data[DATE], "%Y-%m-%d %H:%M:%S")
    line = data[LINE]
    dir = data[DIR]
    lon = data[LON]
    lat = data[LAT]
    mode = data[MODE]
    
    if USER in data.keys():
        user = data[USER]

    #for testing api
    else:
        user = TESTUSER

    #insert data into database
    insert = InsertScan(uuid,date,line,dir,lon,lat,mode,user)
    valid, insertID, match = insert.isSuccessful()

    return jsonify(success=valid, insertID=insertID, match=match)

#api route for boarding and alighting locations selected from map
@app.route('/insertPair', methods=['POST'])
def insertPair():
    data = json.loads(request.form[DATA])
    valid = False
    insertID = -1
    date = datetime.datetime.strptime(data[DATE], "%Y-%m-%d %H:%M:%S")
    line = data[LINE]
    dir = data[DIR]
    on_stop = data[ON_STOP]
    off_stop = data[OFF_STOP]

    if USER in data.keys():
        user = data[USER]
    #for testing api
    else:
        user = TESTUSER

    #insert data into database
    insert = InsertPair(date,line,dir,on_stop,off_stop, user)
    valid, insertID = insert.isSuccessful()
   
    return jsonify(success=valid, insertID=insertID)

