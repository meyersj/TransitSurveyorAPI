from flask import Flask, request, render_template, url_for
from flask.ext.sqlalchemy import SQLAlchemy, orm
#from sqlalchemy import func
from geoalchemy2 import Geometry
from geoalchemy2.elements import WKTElement
from geoalchemy2 import functions as func
import logging, datetime, ast
from logging import FileHandler
import app

base_url = "http://54.244.253.136"



handler = FileHandler('/tmp/app.log')
handler.setLevel(logging.DEBUG)
app.logger.addHandler(handler)

class OnScan(db.Model):
    __tablename__ = 'on_scan'
    #TODO make stop_id reference tm_stops
    id = db.Column(db.Integer, primary_key = True)
    uuid = db.Column(db.Text)
    date = db.Column(db.DateTime)
    
    line = db.Column(db.Text)
    dir = db.Column(db.Text)
    #rte_id = db.Column(db.Integer, db.ForeignKey("tm_routes.gid"), nullable=False)
    
    lon = db.Column(db.Text)
    lat = db.Column(db.Text)
    match = db.Column(db.Boolean)
    geom = db.Column(Geometry(geometry_type='POINT', srid=2913))
    stop_id = db.Column(db.Integer, db.ForeignKey("tm_stops.gid"), nullable=False)
    dist = db.Column(db.Float)
    
    #routes = orm.relationship("Routes")
    stops = orm.relationship("Stops")

    def __init__(self, uuid, date, line, dir, lon, lat, geom, stop_id, dist):
        self.uuid = uuid
        self.date = date
        self.line = line
        self.dir = dir
        self.lon = lon
        self.lat = lat
        self.match = False
        self.geom = geom
        self.stop_id = stop_id
        self.dist = dist
    
    def __repr__(self):
        return '<uuid: %r>' % self.id

class OffScan(db.Model):
    __tablename__ = 'off_scan'
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
    stop_id = db.Column(db.Integer, db.ForeignKey("tm_stops.gid"), nullable=False)
    dist = db.Column(db.Float)
    stops = orm.relationship("Stops")

    def __init__(self, uuid, date, line, dir, lon, lat, match, geom, stop_id, dist):
        self.uuid = uuid
        self.date = date
        self.line = line
        self.dir = dir
        self.lon = lon
        self.lat = lat
        self.match = match
        self.geom = geom
        self.stop_id = stop_id
        self.dist = dist

    def __repr__(self):
        return '<uuid: %r>' % self.id

class OnOff_Pairs(db.Model):
    __tablename__ = 'onoff_pairs'
    id = db.Column(db.Integer, primary_key = True)
    line = db.Column(db.Text)
    dir = db.Column(db.Text)
    on_id = db.Column(db.Integer, db.ForeignKey("on_scan.id"), nullable=False)
    off_id = db.Column(db.Integer, db.ForeignKey("off_scan.id"), nullable=False)
    on = orm.relationship("OnScan")
    off = orm.relationship("OffScan")


    def __init__(self, line, dir, on_id, off_id):
        self.line = line
        self.dir = dir
        self.on_id = on_id
        self.off_id = off_id

class Stops(db.Model):
   __tablename__ = 'tm_stops'
   gid = db.Column(db.Integer, primary_key = True)
   rte = db.Column(db.SmallInteger)
   rte_desc = db.Column(db.Text)
   dir = db.Column(db.SmallInteger)
   dir_desc = db.Column(db.Text)
   stop_name = db.Column(db.Text)
   stop_seq = db.Column(db.Integer)
   stop_id = db.Column(db.Integer)
   geom = db.Column(Geometry(geometry_type='POINT', srid=2913))
   grouping = db.Column(db.Integer)

   def __repr__(self):
       return '<uuid: %r>' % self.stop_id

class Routes(db.Model):
   __tablename__ = 'tm_routes'
   gid = db.Column(db.Integer, primary_key = True)
   rte = db.Column(db.SmallInteger)
   dir = db.Column(db.SmallInteger)
   rte_desc = db.Column(db.Text)
   dir_desc = db.Column(db.Text)
   geom = db.Column(Geometry(geometry_type='MULTILINESTRING', srid=2913))
   def __repr__(self):
       return '<uuid: %r>' % self.rte

db.create_all()

def insertOn(params):
    params = findStop(params)
    insert = OnScan(uuid=params['uuid'], date=params['date'], 
                    line=params['line'], dir=params['dir'],
                    lon=params['lon'], lat=params['lat'],
                    geom=params['geom'], stop_id=params['stop_id'],
                    dist=params['dist'])
    db.session.add(insert)
    db.session.commit()
 
def insertOff(params):
    params = findStop(params)
    match = False
    on_scan = None
    on_scan = OnScan.query.filter_by(uuid=params['uuid'], line=params['line'], dir=params['dir'], match=False)\
                          .order_by(OnScan.date.desc()).first()
    
    #TODO
    """add logic checking for large time discrpency between on and off dates"""
    if on_scan:
        match = True
        on_scan.match = True
    else:
        app.logger.error("off scan did not find matching on scan")

    app.logger.error(params['stop_id'])

    insert = OffScan(uuid=params['uuid'], date=params['date'], 
                     line=params['line'], dir=params['dir'],
                     lon=params['lon'], lat=params['lat'],
                     match=match, geom=params['geom'], 
                     stop_id=params['stop_id'], dist=params['dist'])
    db.session.add(insert)
    db.session.commit()
    
    if match:
        off = OffScan.query.order_by(OffScan.date.desc()).first()
        pair = OnOff_Pairs(line=params['line'], dir=params['dir'], on_id = on_scan.id, off_id=off.id)
        db.session.add(pair)
        db.session.commit()
"""
def findRte(params):
    rte_id = None
    
    rte = Routes.query.filter_by(params['line']=rte, params['dir']=dir).first()
"""


def findStop(params):
    geom = None
    stop_id = None
    dist = None
    try:
        geom = func.ST_Transform(WKTElement('POINT('+params['lon']+' '+params['lat']+')',srid=4326),2913)
        app.logger.error(params['line'])
        near_stop = db.session.query(Stops.gid,
                                     func.ST_Distance(Stops.geom, geom).label("dist"))\
                              .filter_by(rte=int(params['line']), dir=int(params['dir']))\
                              .order_by(Stops.geom.distance_centroid(geom))\
                              .first()
        if near_stop.dist > 1500:
            app.logger.error("nearest stop >500ft away")
        else: 
            dist = near_stop.dist
            stop_id = near_stop.gid
            app.logger.error(stop_id)
            app.logger.error(dist)

    
    except:
        app.logger.error("lat long could not be converted to geom or stopid not found")
    
    params['geom'] = geom
    params['stop_id'] = stop_id
    params['dist'] = dist
    return params 


@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        params = {}
        params['uuid'] = request.form['uuid']
        params['date'] = datetime.datetime.strptime(request.form['date'], "%Y-%m-%d %H:%M:%S")
        params['line'] = request.form['line']
        params['dir'] = request.form['dir']
        params['lon'] = request.form['lon']
        params['lat'] = request.form['lat']
        mode = request.form['mode']
        
        if mode == 'on':
            insertOn(params)
        elif mode == 'off':
            insertOff(params)
    else:
        app.logger.error("mode not 'on' or 'off'")
    
    return "some response"

def getLines():
    routes = db.session.query(Stops.rte, Stops.rte_desc).distinct().all()
    lines = []
    if routes:
        for route in routes:
            lines.append((route.rte, route.rte_desc))

    lines = sorted(lines, key=lambda x: int(x[0]))
    lines.insert(0, ("all", "Display All"))
    return lines

 
@app.route('/stats')
def stats():
    on_results = OnScan.query.order_by(OnScan.line).all()
    off_results = OffScan.query.order_by(OffScan.line).all()

    lines = getLines()
    
    return render_template('lines.html', base_url=base_url, lines=lines)


@app.route('/stats/<in_param>')
def stats_filter(in_param):
    
    lines = getLines()
    if in_param == 'all':
        on_results = OnScan.query.order_by(OnScan.date.desc()).all()
        off_results = OffScan.query.order_by(OffScan.date.desc()).all()
        pair_results = OnOff_Pairs.query.all()
        group_results = db.session\
                          .query(Stops.grouping,
                                 Stops.rte_desc,
                                 Stops.dir_desc, 
                                 db.func.count(OnOff_Pairs.id)\
                                     .label('count'))\
                          .join(OnScan).join(OnOff_Pairs)\
                          .group_by(Stops.grouping,
                                    Stops.rte_desc,
                                    Stops.dir_desc).all()
  
    
    else:
        on_results = OnScan.query.filter_by(line=in_param)\
                           .order_by(OnScan.date.desc()).all()
        off_results = OffScan.query.filter_by(line=in_param)\
                             .order_by(OffScan.date.desc()).all()
        pair_results = OnOff_Pairs.query.filter_by(line=in_param).all()
        group_results = db.session\
                          .query(Stops.grouping,
                                 Stops.rte_desc,
                                 Stops.dir_desc, 
                                 db.func.count(OnOff_Pairs.id)\
                                     .label('count'))\
                          .filter_by(rte=in_param)\
                          .join(OnScan).join(OnOff_Pairs)\
                          .group_by(Stops.grouping,
                                    Stops.rte_desc,
                                    Stops.dir_desc).all()




    return render_template('query.html', on_query=on_results,
                                         off_query=off_results,
                                         pair_query=pair_results,
                                         group_query=group_results)
@app.route('/')
def home():
    return render_template('home.html', base_url=base_url)

@app.route('/map')
def map():
    geojson = {'type': 'FeatureCollection','features': []}

    stops = db.session.query(func.ST_AsGeoJSON(func.ST_Transform(Stops.geom, 4326),10)).filter_by(rte=33,dir=0).all()

   
    for stop in stops:
        geom = ast.literal_eval(str(stop[0]))
        #app.logger.error(stop[0])
        feature_out = {'type':'Feature','geometry':geom,'properties':{'rte': '0'}}
        geojson['features'].append(feature_out)
    return render_template('map.html', base_url=base_url, geojson=geojson)

"""
@app.route('/map/<rte>')
def map_route(rte):
    geojson = {'type': 'FeatureCollection','features': []}
    route = db.session.query(Routes.rte, Routes.rte_desc, func.ST_AsGeoJSON(func.ST_Transform(Routes.geom, 4326),10).label('geom')).filter_by(rte=rte).first()

    if route:
        feature_out = {'type':'Feature','geometry':ast.literal_eval(str(route.geom)),'properties':{'rte':route.rte_desc}}
        geojson['features'].append(feature_out)
    
    return render_template('map.html')
"""

if __name__ == '__main__':
    app.run()
