from flask.ext.sqlalchemy import orm
from geoalchemy2 import Geometry
from api import db

class OnTemp(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    uuid = db.Column(db.Text)
    date = db.Column(db.DateTime)
    line = db.Column(db.Text)
    dir = db.Column(db.Text)
    match = db.Column(db.Boolean)
    geom = db.Column(Geometry(geometry_type='POINT', srid=2913))
   
    def __init__(self, uuid, date, line, dir, geom):
        self.uuid = uuid
        self.date = date
        self.line = line
        self.dir = dir
        self.match = False
        self.geom = geom

    def __repr__(self):
        return '<OnTemp: %r, %r, %r, %r, %r >' %\
            (self.id, self.uuid, self.date, self.line, self.dir)


"""
This table is not necessary
It is being used for initial testing purposes
"""
class OffTemp(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    uuid = db.Column(db.Text)
    date = db.Column(db.DateTime)
    line = db.Column(db.Text)
    dir = db.Column(db.Text)
    match = db.Column(db.Boolean)
    geom = db.Column(Geometry(geometry_type='POINT', srid=2913))
   
    def __init__(self, uuid, date, line, dir, geom):
        self.uuid = uuid
        self.date = date
        self.line = line
        self.dir = dir
        self.match = False
        self.geom = geom

    def __repr__(self):
        return '<OnTemp: %r, %r, %r, %r, %r >' %\
            (self.id, self.uuid, self.date, self.line, self.dir)

"""
Scans is model for a table that holds all on off scans that were linked successfully
"""
class Scans(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    date = db.Column(db.DateTime)
    line = db.Column(db.Text)
    dir = db.Column(db.Text)
    geom = db.Column(Geometry(geometry_type='POINT', srid=2913))
   
    def __init__(self, date, line, dir, geom):
        self.date = date
        self.line = line
        self.dir = dir
        self.geom = geom

    def __repr__(self):
        return '<OnTemp: %r, %r, %r, %r >' %\
            (self.id, self.date, self.line, self.dir)


class OnOffPairs(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    on_id = db.Column(db.Integer, db.ForeignKey("scans.id"), nullable=False)
    off_id = db.Column(db.Integer, db.ForeignKey("scans.id"), nullable=False)
    on = orm.relationship("Scans", foreign_keys=on_id)
    off = orm.relationship("Scans", foreign_keys=off_id)

    def __init__(self, on_id, off_id):
        self.on_id = on_id
        self.off_id = off_id

    def __repr__(self):
        return '<OnOffPairs: id:%r, on_id:%r, off_id:%r >' %\
            (self.id, self.on_id, self.off_id)

class Stops(db.Model):
   __tablename__ = 'tm_route_stops'
   gid = db.Column(db.Integer, primary_key = True)
   rte = db.Column(db.SmallInteger)
   rte_desc = db.Column(db.Text)
   dir = db.Column(db.SmallInteger)
   dir_desc = db.Column(db.Text)
   stop_name = db.Column(db.Text)
   stop_seq = db.Column(db.Integer)
   stop_id = db.Column(db.Integer)
   geom = db.Column(Geometry(geometry_type='POINT', srid=2913))

   def __repr__(self):
       return '<Stops: %r>' % (self.stop_id)

