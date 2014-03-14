from flask import Flask
from flask import request, render_template
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import func
from geoalchemy2 import Geometry
from geoalchemy2.elements import WKTElement
from geoalchemy2.functions import ST_Transform
import logging, datetime, ast
from logging import FileHandler

base_url = "http://54.244.253.136"


app = Flask(__name__)
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)
"""
handler = FileHandler('/tmp/app.log')
handler.setLevel(logging.DEBUG)
app.logger.addHandler(handler)
"""
class OnScan(db.Model):
    #TODO make stop_id reference tm_stops
    id = db.Column(db.Integer, primary_key = True)
    uuid = db.Column(db.Text)
    date = db.Column(db.DateTime)
    line = db.Column(db.Text)
    dir = db.Column(db.Text)
    lon = db.Column(db.Text)
    lat = db.Column(db.Text)
    match = db.Column(db.Boolean)
    geom = db.Column(Geometry(geometry_type='POINT', srid=2913))
    stop_id = db.Column(db.Integer)

    def __init__(self, uuid, date, line, dir, lon, lat, geom, stop_id):
        self.uuid = uuid
        self.date = date
        self.line = line
        self.dir = dir
        self.lon = lon
        self.lat = lat
        self.match = False
        self.geom = geom
        self.stop_id = stop_id    
    def __repr__(self):
        return '<uuid: %r>' % self.id

class OffScan(db.Model):
    #TODO make stop_id reference tm_stops
    id = db.Column(db.Integer, primary_key = True)
    uuid = db.Column(db.Text)
    date = db.Column(db.DateTime)
    line = db.Column(db.Text)
    dir = db.Column(db.Text)
    lon = db.Column(db.Text)
    lat = db.Column(db.Text)
    match = db.Column(db.Boolean)
    geom = db.Column(Geometry(geometry_type='POINT', srid=2913))
    stop_id = db.Column(db.Integer)

    def __init__(self, uuid, date, line, dir, lon, lat, match, geom, stop_id):
        self.uuid = uuid
        self.date = date
        self.line = line
        self.dir = dir
        self.lon = lon
        self.lat = lat
        self.match = match
        self.geom = geom
        self.stop_id = stop_id

    def __repr__(self):
        return '<uuid: %r>' % self.id

class OnOff_Pairs(db.Model):
    __tablename__ = 'onoff_pairs'
    id = db.Column(db.Integer, primary_key = True)
    line = db.Column(db.Text)
    dir = db.Column(db.Text)
    on_date = db.Column(db.DateTime)
    on_lon = db.Column(db.Text)
    on_lat = db.Column(db.Text)
    on_geom = db.Column(Geometry(geometry_type='POINT', srid=2913))
    on_stop_id = db.Column(db.Integer)
    off_date = db.Column(db.DateTime)
    off_lon = db.Column(db.Text)
    off_lat = db.Column(db.Text)
    off_geom = db.Column(Geometry(geometry_type='POINT', srid=2913))
    off_stop_id = db.Column(db.Integer)

    def __init__(self, line, dir, on_date, on_lon, on_lat, on_geom, on_stop_id,
                                  off_date, off_lon, off_lat, off_geom, off_stop_id):
        self.line = line
        self.dir = dir
        self.on_date = on_date
        self.on_lon = on_lon
        self.on_lat = on_lat
        self.on_geom = on_geom
        self.on_stop_id = on_stop_id
        self.off_date = off_date
        self.off_lon = off_lon
        self.off_lat = off_lat
        self.off_geom = off_geom
        self.off_stop_id = off_stop_id

class Stops(db.Model):
   __tablename__ = 'tm_stops'
   gid = db.Column(db.Integer, primary_key = True)
   rte = db.Column(db.SmallInteger)
   dir = db.Column(db.SmallInteger)
   stop_seq = db.Column(db.Integer)
   stop_id = db.Column(db.Integer)
   geom = db.Column(Geometry(geometry_type='POINT', srid=2913))

   def __repr__(self):
       return '<uuid: %r>' % self.stop_id


db.create_all()

@app.route('/submit', methods=['POST'])
def post():
    if request.method == 'POST':
        uuid = request.form['uuid']
        date = request.form['date']
        line = request.form['line']
        dir = request.form['dir']
        lon = request.form['lon']
        lat = request.form['lat']
        mode = request.form['mode']
        date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        geom = None
        stop_id = None 
        try:
            geom = ST_Transform(WKTElement('POINT('+lon+' '+lat+')',srid=4326),2913)
            near_stop = Stops.query.filter_by(rte=int(line))\
                             .order_by(Stops.geom.distance_box(geom))\
                             .first()
            stop_id = near_stop.stop_id
        except:
            app.logger.error("lat long could not be converted to geom or stopid not found")
   
    
        add = None
        if mode == 'on':
            add = OnScan(uuid=uuid, date=date, line=line, dir=dir, lon=lon, lat=lat, geom=geom, stop_id=stop_id)
        if mode == 'off':
            on_scan = None
            on_scan = OnScan.query.filter_by(uuid=uuid, line=line, dir=dir, match=False).order_by(OnScan.date.desc()).first()
      
            #TODO
            """add logic checking for large time discrpency between on and off dates"""

            if on_scan:
                match = True
                on_scan.match = True
                pair = OnOff_Pairs(line=line, dir=dir,
                                   on_date=on_scan.date,
                                   on_lon=on_scan.lon,
                                   on_lat=on_scan.lat,
                                   on_geom = on_scan.geom,
                                   on_stop_id = on_scan.stop_id,
                                   off_date=date,
                                   off_lon=lon,
                                   off_lat=lat,
                                   off_geom=geom,
                                   off_stop_id=stop_id)
                db.session.add(pair)
            else:
                match = False
                app.logger.error("submit: off scan did not find matching on scan")
                app.logger.error("        " + str(uuid) + " " + str(date))

            add = OffScan(uuid=uuid, date=date, line=line, dir=dir, lon=lon, lat=lat, match=match, geom=geom, stop_id=stop_id)

        db.session.add(add)
        db.session.commit()
    else:
        app.logger.error("request not post")
  
    return "some response"
 
@app.route('/stats')
def stats():
    on_results = OnScan.query.order_by(OnScan.line).all()
    off_results = OffScan.query.order_by(OffScan.line).all()

    lines = []
    for row in on_results:
        lines.append(int(row.line))
    for row in off_results:
        lines.append(int(row.line))

    lines = sorted(list(set(lines)))
    return render_template('lines.html', base_url=base_url, lines=lines)


@app.route('/stats/<in_param>')
def stats_filter(in_param):
    if in_param == 'all':
        on_results = OnScan.query.order_by(OnScan.date.desc()).all()
        off_results = OffScan.query.order_by(OffScan.date.desc()).all()
        pair_results = OnOff_Pairs.query.all()

    else:
        on_results = OnScan.query.filter_by(line=in_param)\
                           .order_by(OnScan.date.desc()).all()
        off_results = OffScan.query.filter_by(line=in_param)\
                             .order_by(OffScan.date.desc()).all()
        pair_results = OnOff_Pairs.query.filter_by(line=in_param).all()

    return render_template('query.html', base_url=base_url, 
                                         on_query=on_results,
                                         off_query=off_results,
                                         pair_query=pair_results)

@app.route('/')
def home():
    return render_template('home.html', base_url=base_url)

@app.route('/map')
def map():
    geojson = {'type': 'FeatureCollection','features': []}

    stops = db.session.query(func.ST_AsGeoJSON(func.ST_Transform(Stops.geom, 4326),10)).filter_by(rte=12,dir=0)

    for stop in stops:
        geom = ast.literal_eval(str(stop[0]))
        feature_out = {'type':'Feature','geometry':geom,'properties':{'rte': '0'}}
        geojson['features'].append(feature_out)
        app.logger.debug(geojson)
    return render_template('map.html', base_url=base_url, points=geojson)



if __name__ == '__main__':
    app.run()
