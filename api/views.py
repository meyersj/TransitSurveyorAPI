from flask import request
from flask import jsonify
from api import app, db
from insert import InsertScan, InsertPair
from models import Users
from crypter import Crypter
import datetime
import json

DATA = "data"
USERNAME = "username"
PASSWORD = "password"
KEYS = "KEYS"

UUID = "uuid"
DATE = "date"
LINE = "rte"
DIR = "dir"
LON = "lon"
LAT = "lat"
MODE = "mode"
ON_STOP = "on_stop"
OFF_STOP = "off_stop"


@app.route('/')
def index():
    return "hello"    


@app.route('/createUser', methods=['POST'])
def createUser():    
    crypter = Crypter(app.config[KEYS])
    first = request.form['first']
    last = request.form['last']
    username = request.form['username']
    password = request.form['password']
    password_hash = crypter.Encrypt(password)

    new_user = Users(first, last, username, password_hash)
    db.session.add(new_user)
    db.session.commit()

    return jsonify(success=True)


def verify_user(username, password):
    user_match = False
    password_match = False

    crypter = Crypter(app.config[KEYS])
   
    user = Users.query.filter_by(username=username).first()
   
    if user:
        user_match = True
        if password == crypter.Decrypt(user.password_hash):
            password_match = True
            app.logger.debug("password did not match")
    else:
        app.logger.error("user name did not match") 

    return user_match, password_match


@app.route('/verifyUser', methods=['POST'])
def verifyUser():
    crypter = Crypter(app.config[KEYS])
    data_encrypt = request.form[DATA]
    data = json.loads(crypter.Decrypt(data_encrypt))
    
    username = data[USERNAME]
    password = data[PASSWORD]
    
    user_match, password_match = verify_user(username, password)  
    
    return jsonify(user_match=user_match, password_match=password_match)
   



#api route for on off locations from scanner
@app.route('/insertScan', methods=['POST'])
def insertScan():
    valid = False
    insertID = -1

    if request.method == 'POST':
        uuid = request.form[UUID]
        date = datetime.datetime.strptime(request.form[DATE], "%Y-%m-%d %H:%M:%S")
        line = request.form[LINE]
        dir = request.form[DIR]
        lon = request.form[LON]
        lat = request.form[LAT]
        mode = request.form[MODE]

        #insert data into database
        insert = InsertScan(uuid,date,line,dir,lon,lat,mode)
        valid, insertID, match = insert.isSuccessful()

    return jsonify(success=valid, insertID=insertID, match=match)

#api route for boarding and alighting locations selected from map
@app.route('/insertPair', methods=['POST'])
def insertPair():
    valid = False
    insertID = -1
    if request.method == 'POST':
        date = datetime.datetime.strptime(request.form[DATE], "%Y-%m-%d %H:%M:%S")
        line = request.form[LINE]
        dir = request.form[DIR]
        on_stop = request.form[ON_STOP]
        off_stop = request.form[OFF_STOP]

        #insert data into database
        insert = InsertPair(date,line,dir,on_stop,off_stop)
        valid, insertID = insert.isSuccessful()

    
    return jsonify(success=valid, insertID=insertID)




