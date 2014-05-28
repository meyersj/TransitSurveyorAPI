from web_app import app
from web_app import db
from web_app import models
from geoalchemy2.elements import WKTElement
from geoalchemy2 import functions as func

class InsertScan():
    #passed params
    uuid = None
    date = None
    line = None
    dir = None
    lon = None
    lat = None
    mode = None
    
    #created params
    geom = None
    stop_id = None
    dist = None
    geom = None
    valid = True

    def __init__(self,uuid,date,line,dir,lon,lat,mode):
        self.uuid = uuid
        self.date = date
        self.line = line
        self.dir = dir
        self.lon = lon
        self.lat = lat
        self.mode = mode
        self.isValid = True

        #query for nearest stop to coordinates
        self.findNearStop()

        if self.isValid:
            if self.mode == 'on':
                self.insertOn()
            elif self.mode == 'off':
                self.insertOff()

    def findNearStop(self):
        wkt = 'POINT('+self.lon+' '+self.lat+')'
        
        try:
            self.geom = func.ST_Transform(WKTElement(wkt,srid=4326),2913)
            near_stop = db.session.query(models.Stops.gid,
                func.ST_Distance(models.Stops.geom, self.geom).label("dist"))\
                    .filter_by(rte=int(self.line), dir=int(self.dir))\
                    .order_by(models.Stops.geom.distance_centroid(self.geom))\
                    .first()

            if near_stop:
                self.stop_id = near_stop.gid
                self.dist = near_stop.dist
            else:
                self.isValid = False
        
        except Exception as e:
            self.isValid = False
            app.logger.error("Exception thrown in findNearStop: "+str(e))

    def insertOn(self):
        insert = models.OnScan(uuid=self.uuid, date=self.date, 
                               line=self.line, dir=self.dir,
                               geom=self.geom, stop_id = self.stop_id,
                               dist=self.dist)
        db.session.add(insert)
        db.session.commit()

    def insertOff(self):
        match = False
        on_scan = None
        on_scan = models.OnScan.query.filter_by(uuid=self.uuid, line=self.line, dir=self.dir, match=False)\
                              .order_by(models.OnScan.date.desc()).first()
        
        app.logger.debug(on_scan)

        if on_scan:
            match = True
            on_scan.match = True
        else:
            app.logger.error("off scan did not find matching on scan")
        
        insert = models.OffScan(uuid=self.uuid, date=self.date, 
                               line=self.line, dir=self.dir,
                               geom=self.geom, stop_id = self.stop_id,
                               dist=self.dist, match=match)
        db.session.add(insert)
        db.session.commit()
        
        if match:
            off = models.OffScan.query.order_by(models.OffScan.date.desc()).first()
            pair = models.OnOffPairs(line=self.line, dir=self.dir, on_id = on_scan.id, off_id=off.id)
            db.session.add(pair)
            db.session.commit()
