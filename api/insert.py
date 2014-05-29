from api import app, db, models
from geoalchemy2.elements import WKTElement
from geoalchemy2 import functions as func

ON = "ON"
OFF = "OFF"

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
        
        self.__getGeom()
        if self.isValid:
            if self.mode == ON:
                self.isValid = self.__insertOn()
            elif self.mode == OFF:
                self.isValid = self.__insertOff()
            else:
                self.isValid = False

    """convert latitude-longitude coordinates to geometry in Oregon State Plane North
    """
    def __getGeom(self):
        wkt = 'POINT('+self.lon+' '+self.lat+')'
        
        try:
            self.geom = func.ST_Transform(WKTElement(wkt,srid=4326),2913)
        except Exception as e:
            self.isValid = False
            msg = "failed to convert lat {0} lon {1} to geom: "\
                .format(self.lat,self.lon) + e
            app.logger.error(e)

    """insert into temp ON table
    """
    def __insertOn(self):
        insert = models.OnTemp(uuid=self.uuid, date=self.date, 
                               line=self.line, dir=self.dir,
                               geom=self.geom)
        
        db.session.add(insert)
        db.session.commit()
        return True

    """match OFF scan with most recent ON scan with same UUID
    if a match is found insert ON and OFF pairs into Scans table
    and insert each of those id's into OnOffPairs table
    """
    def __insertOff(self):
        match = False
        on = None
        on = models.OnTemp.query.filter_by(uuid=self.uuid,
                                           line=self.line,
                                           dir=self.dir,
                                           match=False)\
                                .order_by(models.OnTemp.date.desc()).first()

        if on:
            match = True
            on.match = True
          
            #insert on off records into Scans
            insertOn = models.Scans(on.date, on.line, on.dir, on.geom)
            insertOff = models.Scans(self.date, self.line, self.dir, self.geom)
            db.session.add(insertOn)
            db.session.add(insertOff)
            db.session.commit()    
            
            #insert on and off ids into OnOffPairs
            insertPair = models.OnOffPairs(insertOn.id, insertOff.id)
            db.session.add(insertPair)
            db.session.commit()

        else:
            app.logger.error("Did not find matching ON scan")


        #for initial testing insert into OffTemp
        #in production this will not be needed
        insertOffTemp = models.OffTemp(uuid=self.uuid, date=self.date, 
                                line=self.line, dir=self.dir,
                                geom=self.geom, match=match)
        
        db.session.add(insertOffTemp)
        db.session.commit()

        return True

    def isSuccessful(self):
        return self.isValid
            
    """
    ************************************
    Do this in post processing instead??
    ************************************
    """    

    """
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
            app.logger.error(e)
    """
