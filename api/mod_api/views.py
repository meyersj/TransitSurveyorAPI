# Copyright © 2015 Jeffrey Meyers
# This program is released under the "MIT License".
# Please see the file COPYING in the source
# distribution of this software for license terms.

import datetime
import json
import logging
import hashlib

from flask import Blueprint, request, jsonify
from api import app, db, debug

from sqlalchemy import func as sql_func
from geoalchemy2.elements import WKTElement
from geoalchemy2 import functions as func
import models

from insert import InsertScan, InsertPair
from models import Users

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
ON_REVERSED = "on_reversed"
OFF_REVERSED = "off_reversed"
USER = "user_id"
SALT = "SALT"
TESTUSER = "testuser"


mod_api = Blueprint('api', __name__, url_prefix='/api')

@mod_api.route('/')
def index():
    return "API Module"

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


@mod_api.route('/verifyUser', methods=['POST'])
def verifyUser():
    cred = json.loads(request.form[CREDENTIALS])
    username = cred[USERNAME]
    password = cred[PASSWORD]
    user_match, password_match,user_id = verify_user(username, password)  
    return jsonify(user_match=user_match, password_match=password_match, user_id=user_id)


#api route for on off locations from scanner
@mod_api.route('/insertScan', methods=['POST'])
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
@mod_api.route('/insertPair', methods=['POST'])
def insertPair():
    data = json.loads(request.form[DATA])
    valid = False
    insertID = -1
    date = datetime.datetime.strptime(data[DATE], "%Y-%m-%d %H:%M:%S")
    line = data[LINE]
    dir = data[DIR]
    on_stop = data[ON_STOP]
    off_stop = data[OFF_STOP]
    on_reversed = data[ON_REVERSED]
    off_reversed = data[OFF_REVERSED]

    if USER in data.keys():
        user = data[USER]
    #for testing api
    else:
        user = TESTUSER

    #insert data into database
    insert = InsertPair(date, line, dir, on_stop, off_stop, user, on_reversed, off_reversed)
    valid, insertID = insert.isSuccessful()
   
    return jsonify(success=valid, insertID=insertID)

@mod_api.route('/stopLookup', methods=['POST'])
def stopLookup():
    data = json.loads(request.form[DATA])
    geom = getGeom(data[LAT], data[LON])
    stop_name, stop_seq, error = findNearStop(geom, data[LINE], data[DIR]) 
    return jsonify(error=error, stop_seq_rem=stop_seq, stop_name=stop_name)

def getGeom(lat, lon):
    geom = None
    try:
        wkt = 'POINT('+lon+' '+lat+')'
        geom = func.ST_Transform(WKTElement(wkt,srid=4326),2913)
    except Exception as e:
        app.logger.warn(e)
    return geom

def findNearStop(geom, line, dir):
    stop_seq = None
    stop_name = None
    error = True
    if geom is None:
        return stop_name, error
    try:
        near_stop = db.session.query(
            models.Stops.gid, models.Stops.stop_name, models.Stops.stop_seq,
            func.ST_Distance(models.Stops.geom, geom).label("dist"))\
            .filter_by(rte=int(line), dir=int(dir))\
            .order_by(models.Stops.geom.distance_centroid(geom))\
            .first()
        if near_stop:
            stop_name = near_stop.stop_name
            stop_seq = near_stop.stop_seq
            max_stop = db.session.query(sql_func.max(models.Stops.stop_seq))\
                .filter_by(rte=int(line), dir=int(dir)).first()
            
            stop_seq = int((max_stop[0] - stop_seq) / 50)
            error = False

    except Exception as e:
        app.logger.warn("Exception thrown in findNearStop: " + str(e))

    return stop_name, stop_seq, error
