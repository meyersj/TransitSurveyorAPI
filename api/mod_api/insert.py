from api import app, db

import models
from geoalchemy2.elements import WKTElement
from geoalchemy2 import functions as func

ON = "on"
OFF = "off"

class InsertScan():
    #passed params
    uuid = None
    date = None
    line = None
    dir = None
    lon = None
    lat = None
    mode = None
    user = None

    #created params
    geom = None
    valid = True
    insertID = None
    match = False

    def __init__(self,uuid,date,line,dir,lon,lat,mode,user):
        self.uuid = uuid
        self.date = date
        self.line = line
        self.dir = dir
        self.lon = lon
        self.lat = lat
        self.mode = mode
        self.isValid = True
        self.user = user
        
        self.__getGeom()
        if self.isValid:
            if self.mode == ON:
                self.isValid, self.insertID = self.__insertOn()
            elif self.mode == OFF:
                self.isValid, self.insertID, self.match = self.__insertOff()
            else:
                self.isValid = False

    """convert latitude-longitude coordinates to geometry in Oregon State Plane North
    """
    def __getGeom(self):
        
        if self.lon and self.lat:
            try:
                wkt = 'POINT('+self.lon+' '+self.lat+')'
                self.geom = func.ST_Transform(WKTElement(wkt,srid=4326),2913)
            except Exception as e:
                self.isValid = False
                msg = "failed to convert lat {0} lon {1} to geom: "\
                    .format(self.lat,self.lon) + e
                app.logger.warn(e)
        else:
            app.logger.warn("lat or lon does not exist, user=" + self.user)

    """insert into temp ON table
    """
    def __insertOn(self):
        insertID = -1
        insert = models.OnTemp(uuid=self.uuid, date=self.date, 
                               line=self.line, dir=self.dir,
                               geom=self.geom, user_id=self.user)
        
        db.session.add(insert)
        db.session.commit()
        insertID = insert.id

        return True, insertID

    """match OFF scan with most recent ON scan with same UUID
    if a match is found insert ON and OFF pairs into Scans table
    and insert each of those id's into OnOffPairs table
    """
    def __insertOff(self):
        match = False
        insertID = -1
        on = None

        # fetch all records
        # grab first to match up and delete the rest if they exist
        on = models.OnTemp.query.filter_by(
            uuid=self.uuid, line=self.line, dir=self.dir,
            match=False).order_by(models.OnTemp.date.desc())

        if on.count() > 0:
            iter_on = iter(on)
            # grab first 
            on = next(iter_on)
            # delete the rest
            for record in iter_on:
                db.session.delete(record)

            match = True
            on.match = True

            on_stop = self.findNearStop(on.geom)
            off_stop = self.findNearStop(self.geom)
          
            #insert on off records into Scans
            insertOn = models.Scans(
                on.date, on.line, on.dir, on.geom, on.user_id, on_stop)
            insertOff = models.Scans(
                self.date, self.line, self.dir, self.geom, self.user, off_stop)
            
            db.session.add(insertOn)
            db.session.add(insertOff)
            db.session.commit()    
            
            #insert on and off ids into OnOffPairs
            insertPair = models.OnOffPairs_Scans(insertOn.id, insertOff.id)
            db.session.add(insertPair)
            db.session.commit()

        else:
            app.logger.warn("did not find matching ON scan")

        #for initial testing insert into OffTemp
        #in production this will not be needed
        insertOffTemp = models.OffTemp(
            uuid=self.uuid, date=self.date, line=self.line, dir=self.dir,
            geom=self.geom, user_id=self.user, match=match)
        
        db.session.add(insertOffTemp)
        db.session.commit()
        insertID = insertOffTemp.id

        return True, insertID, match

    def isSuccessful(self):
        return self.isValid, self.insertID, self.match
            

    def findNearStop(self, geom):
        stop_id = None

        try:
            near_stop = db.session.query(models.Stops.gid,
                func.ST_Distance(models.Stops.geom, geom).label("dist"))\
                .filter_by(rte=int(self.line), dir=int(self.dir))\
                .order_by(models.Stops.geom.distance_centroid(geom))\
                .first()

            if near_stop:
                stop_id = near_stop.gid
        
        except Exception as e:
            app.logger.warn("Exception thrown in findNearStop: " + str(e))

        return stop_id


class InsertPair():
    #passed params
    date = None
    line = None
    dir = None
    on_stop = None
    off_stop = None 
    user = None
    on_reversed = None
    off_reversed = None
    #created params
    valid = True
    insertID = -1

    def __init__(self,date,line,dir,on_stop,off_stop, user, on_reversed, off_reversed):
        self.date = date
        self.line = line
        self.dir = dir
        self.on_stop = on_stop
        self.off_stop = off_stop
        self.user = user
        self.on_reversed = on_reversed
        self.off_reversed = off_reversed
        self.isValid = True
        self.__insertPair()      

    def reverse_direction(self):
        if self.dir == "1":
            return "0"
        else:
            return "1"

    def __insertPair(self):
        on_dir = self.dir
        off_dir = self.dir

        if self.on_reversed == "true":
            on_dir = self.reverse_direction()
        if self.off_reversed == "true":
            off_dir = self.reverse_direction()
       
        
        on_stop = models.Stops.query.filter_by(
            rte=self.line, dir=on_dir, stop_id=self.on_stop).first()

        off_stop = models.Stops.query.filter_by(
            rte=self.line, dir=off_dir, stop_id=self.off_stop).first()

        if on_stop and off_stop:
            insert = models.OnOffPairs_Stops(
                self.date, self.line, self.dir,
                on_stop.gid, off_stop.gid,self.user)

            db.session.add(insert)
            db.session.commit()
            self.insertID = insert.id 
 
        else:
            self.valid = False
            if not on_stop:
                app.logger.error(
                    "On stop_id did not match have match in tm_route_stops table")
            else:
                app.logger.error(
                    "Off stop_id did not match have match in tm_route_stops table")

    def isSuccessful(self):
        return self.valid, self.insertID
    
