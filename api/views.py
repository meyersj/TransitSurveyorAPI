from flask import request
from flask import jsonify
from api import app, db
from insert import InsertScan, InsertPair
from models import Users
from crypter import Crypter
import datetime
import json
import logging

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
USER = "user"

@app.route('/')
def index():
    return "Testing"


def verify_user(username, password):
    user_match = False
    password_match = False
    user_id = -1

    crypter = Crypter(app.config[KEYS])
    user = Users.query.filter_by(username=username).first()
   
    if user:
        user_match = True
        if password == crypter.Decrypt(user.password_hash):
            password_match = True
            user_id = user.id
    else:
        app.logger.debug("User name did not match") 

    return user_match, password_match, user_id


@app.route('/verifyUser', methods=['POST'])
def verifyUser():
    crypter = Crypter(app.config[KEYS])
    cred_encrypt = request.form[CREDENTIALS]
    cred_decrypt = json.loads(crypter.Decrypt(cred_encrypt))
 
    username = cred_decrypt[USERNAME]
    password = cred_decrypt[PASSWORD]
    
    user_match, password_match,user_id = verify_user(username, password)  
    data = json.dumps({"user_match":user_match,
                       "password_match":password_match,
                       "user_id":user_id})

    
    if app.debug == True:
        return data
    else:
        data_encrypt = crypter.Encrypt(data)
        return data_encrypt

#api route for on off locations from scanner
@app.route('/insertScan', methods=['POST'])
def insertScan():
    crypter = Crypter(app.config[KEYS])
    data_encrypt = request.form[DATA]
    data_decrypt = json.loads(crypter.Decrypt(data_encrypt))

    app.logger.debug(data_decrypt)

    valid = False
    insertID = -1

    uuid = data_decrypt[UUID]
    date = datetime.datetime.strptime(data_decrypt[DATE], "%Y-%m-%d %H:%M:%S")
    line = data_decrypt[LINE]
    dir = data_decrypt[DIR]
    lon = data_decrypt[LON]
    lat = data_decrypt[LAT]
    mode = data_decrypt[MODE]

    
    if USER in data_decrypt.keys():
        user = data_decrypt[USER]

    #for testing api
    else:
        test_user = Users.query.filter_by(username = "testuser").first()
        app.logger.debug(test_user)
        user = test_user.id

    #insert data into database
    insert = InsertScan(uuid,date,line,dir,lon,lat,mode,user)
    valid, insertID, match = insert.isSuccessful()

    return jsonify(success=valid, insertID=insertID, match=match)

#api route for boarding and alighting locations selected from map
@app.route('/insertPair', methods=['POST'])
def insertPair():
    crypter = Crypter(app.config[KEYS])
    data_encrypt = request.form[DATA]
    data_decrypt = json.loads(crypter.Decrypt(data_encrypt))

    valid = False
    insertID = -1
    date = datetime.datetime.strptime(data_decrypt[DATE], "%Y-%m-%d %H:%M:%S")
    line = data_decrypt[LINE]
    dir = data_decrypt[DIR]
    on_stop = data_decrypt[ON_STOP]
    off_stop = data_decrypt[OFF_STOP]

    if USER in data_decrypt.keys():
        user = data_decrypt[USER]
    #for testing api
    else:
        test_user = Users.query.filter_by(username = "testuser").first()
        app.logger.debug(test_user)
        user = test_user.id

    #insert data into database
    insert = InsertPair(date,line,dir,on_stop,off_stop, user)
    valid, insertID = insert.isSuccessful()

    #data = json.dumps({"user_match":user_match, "password_match":password_match, "user_id":user_id})
   
    return jsonify(success=valid, insertID=insertID)

