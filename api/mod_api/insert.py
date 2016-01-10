# Copyright (C) 2015 Jeffrey Meyers
# This program is released under the "MIT License".
# Please see the file COPYING in the source
# distribution of this software for license terms.

from api import app, db

import models
from geoalchemy2.elements import WKTElement
from geoalchemy2 import functions as func


ON = "on"
OFF = "off"


#convert latitude-longitude coordinates to geometry object
# in Oregon State Plane North EPSG:2913
def buildGeom(lat, lon):
    success = False
    geom = None
    if lat and lon:
        try:
            wkt = 'POINT({0} {1})'.format(lon, lat)
            geom = func.ST_Transform(WKTElement(wkt,srid=4326),2913)
            success = True
        except Exception as e:
            msg = "failed to convert lat {0} lon {1} to geom: ".format(lat,lon)
            app.logger.warn(msg)
    return success, geom 


class InsertScan():
    insertID = -1
    match = False

    def __init__(self,uuid="",date="",rte="",dir="",lon="",lat="",mode="",user_id=""):
        self.uuid = uuid
        self.date = date
        self.rte = rte
        self.dir = dir
        self.lon = lon
        self.lat = lat
        self.mode = mode
        self.isValid = True
        self.user = user_id
        
        self.isValid, self.geom = buildGeom(self.lat, self.lon)
        if self.isValid:
            if self.mode == ON:
                self.isValid, self.insertID = self.__insertOn()
            elif self.mode == OFF:
                self.isValid, self.insertID, self.match = self.__insertOff()
            else:
                self.isValid = False

    """insert into temp ON table
    """
    def __insertOn(self):
        insertID = -1
        insert = models.OnTemp(
            uuid=self.uuid, 
            date=self.date, 
            rte=self.rte,
            dir=self.dir,
            geom=self.geom,
            user_id=self.user
        )
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
            uuid=self.uuid, rte=self.rte, dir=self.dir,
            match=False).order_by(models.OnTemp.date.desc())

        if on.count() > 0:
            iter_on = iter(on)
            # grab most recent, then delete the rest 
            on = next(iter_on)
            for record in iter_on: db.session.delete(record)

            match = True
            on.match = True

            on_stop = self.findNearStop(on.geom)
            off_stop = self.findNearStop(self.geom)
          
            #insert on off records into Scans
            insertOn = models.Scans(
                on.date, on.rte, on.dir, on.geom, on.user_id, on_stop)
            insertOff = models.Scans(
                self.date, self.rte, self.dir, self.geom, self.user, off_stop)
            
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
            uuid=self.uuid, date=self.date, rte=self.rte, dir=self.dir,
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
                .filter_by(rte=int(self.rte), dir=int(self.dir))\
                .order_by(models.Stops.geom.distance_centroid(geom))\
                .first()
            if near_stop:
                stop_id = near_stop.gid
        except Exception as e:
            app.logger.warn("Exception thrown in findNearStop: " + str(e))
        return stop_id


class InsertPair():
    insertID = -1

    def __init__(self,date="",rte="",dir="",on_stop="",off_stop="",
                    user_id="",on_reversed="",off_reversed=""):
        self.date = date
        self.rte = rte
        self.dir = dir
        self.on_stop = on_stop
        self.off_stop = off_stop
        self.user = user_id
        self.on_reversed = on_reversed
        self.off_reversed = off_reversed
        self.isValid = True
        self.__insertPair()      

    def reverse_direction(self):
        if self.dir == "1": return "0"
        else: return "1"

    def __insertPair(self):
        on_dir = self.dir
        off_dir = self.dir

        if self.on_reversed == "true":
            on_dir = self.reverse_direction()
        if self.off_reversed == "true":
            off_dir = self.reverse_direction()
       
        on_stop = models.Stops.query.filter_by(
            rte=self.rte, dir=on_dir, stop_id=self.on_stop).first()
        off_stop = models.Stops.query.filter_by(
            rte=self.rte, dir=off_dir, stop_id=self.off_stop).first()

        if on_stop and off_stop:
            insert = models.OnOffPairs_Stops(
                self.date, self.rte, self.dir,
                on_stop.gid, off_stop.gid,self.user)
            db.session.add(insert)
            db.session.commit()
            self.insertID = insert.id 
        else:
            self.isValid = False
            if not on_stop:
                app.logger.error(
                    "On stop_id did not find have match in stops table")
            else:
                app.logger.error(
                    "Off stop_id did not find have match in stops table")

    def isSuccessful(self):
        return self.isValid, self.insertID
    
