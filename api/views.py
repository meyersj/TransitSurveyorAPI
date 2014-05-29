from flask import request
from flask import jsonify
from api import app
from insert import InsertScan
import datetime

UUID = "UUID"
DATE = "DATE"
LINE = "LINE"
DIR = "DIR"
LON = "LON"
LAT = "LAT"
MODE = "MODE"

@app.route('/insert', methods=['POST'])
def submit():
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

    return jsonify(success=str(success))
