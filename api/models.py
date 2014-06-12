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


class OnOffPairs_Scans(db.Model):
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

class OnOffPairs_Stops(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    date = db.Column(db.DateTime)
    line = db.Column(db.Text)
    dir = db.Column(db.Text)
    #NOTE see nots from fixme above Stops model
    on_stop = db.Column(db.Integer, db.ForeignKey("tm_route_stops.gid"), nullable=False)
    off_stop = db.Column(db.Integer, db.ForeignKey("tm_route_stops.gid"), nullable=False)
    on = orm.relationship("Stops", foreign_keys=on_stop)
    off = orm.relationship("Stops", foreign_keys=off_stop)

    def __init__(self, date, line, dir, on_stop, off_stop):
        self.date = date
        self.line = line
        self.dir = dir
        self.on_stop = on_stop
        self.off_stop = off_stop

    def __repr__(self):
        return '<OnOffPairs: id:%r, on_id:%r, off_id:%r >' %\
            (self.id, self.on_stop, self.off_stop)


class Users(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    first = db.Column(db.Text)
    last = db.Column(db.Text)
    username = db.Column(db.Text)
    password_hash = db.Column(db.Text)

    def __init__(self, first, last, username, password_hash):
        self.first = first
        self.last = last
        self.username = username
        self.password_hash = password_hash

    def __repr__(self):
        return '<User: Name: %r %r, Username:%r >' %\
            (self.first, self.last, self.username)


#NOTE
"""
there are 9 records where rte+dir+stop_id is not distinct
the stop_seq is different
determine if these stops are on any of the routes to be surveyed

when inserting records into OnOffPairs we may get more than on gid back
using the above conditions

we will take first gid as for our purposes stop sequence does not matter
""" 
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

