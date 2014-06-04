from flask import request
from flask import jsonify
from api import app
from insert import InsertScan, InsertPair
import datetime

UUID = "UUID"
DATE = "DATE"
LINE = "LINE"
DIR = "DIR"
LON = "LON"
LAT = "LAT"
MODE = "MODE"
ON_STOP = "ON_STOP"
OFF_STOP = "OFF_STOP"

@app.route('/')
def index():
    return "Test"

#api route for on off locations from scanner
@app.route('/insertScan', methods=['POST'])
def insertScan():
    success = False
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
        success = insert.isSuccessful()

    return jsonify(success=success)

#api route for boarding and alighting locations selected from map
@app.route('/insertPair', methods=['POST'])
def insertPair():
    success = False
    if request.method == 'POST':
        date = datetime.datetime.strptime(request.form[DATE], "%Y-%m-%d %H:%M:%S")
        line = request.form[LINE]
        dir = request.form[DIR]
        on_stop = request.form[ON_STOP]
        off_stop = request.form[OFF_STOP]

        #insert data into database
        insert = InsertPair(date,line,dir,on_stop,off_stop)
        success = insert.isSuccessful()

    
    return jsonify(success=success)

