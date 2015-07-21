# Copyright (C) 2015 Jeffrey Meyers
# This program is released under the "MIT License".
# Please see the file COPYING in the source
# distribution of this software for license terms.

from flask.ext.sqlalchemy import orm
from geoalchemy2 import Geometry
from api import db

class OnTemp(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    uuid = db.Column(db.Text)
    date = db.Column(db.DateTime)
    rte = db.Column(db.Integer)
    dir = db.Column(db.Integer)
    match = db.Column(db.Boolean)
    geom = db.Column(Geometry(geometry_type='POINT', srid=2913))
    user_id = db.Column(db.Text)
   
    def __init__(self, uuid, date, rte, dir, geom, user_id):
        self.uuid = uuid
        self.date = date
        self.rte = rte
        self.dir = dir
        self.match = False
        self.geom = geom
        self.user_id = user_id

    def __repr__(self):
        return '<OnTemp: %r, %r, %r, %r, %r >' %\
            (self.id, self.uuid, self.date, self.rte, self.dir)


"""
This table is not necessary
It is being used for initial testing purposes
"""
class OffTemp(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    uuid = db.Column(db.Text)
    date = db.Column(db.DateTime)
    rte = db.Column(db.Integer)
    dir = db.Column(db.Integer)
    match = db.Column(db.Boolean)
    geom = db.Column(Geometry(geometry_type='POINT', srid=2913))
    user_id = db.Column(db.Text)
   
    def __init__(self, uuid, date, rte, dir, geom, user_id, match):
        self.uuid = uuid
        self.date = date
        self.rte = rte
        self.dir = dir
        self.match = match
        self.geom = geom
        self.user_id = user_id

    def __repr__(self):
        return '<OnTemp: %r, %r, %r, %r, %r >' %\
            (self.id, self.uuid, self.date, self.rte, self.dir)

"""
Scans is model for a table that holds all on off scans that were linked successfully
"""
class Scans(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    date = db.Column(db.DateTime)
    rte = db.Column(db.Integer)
    dir = db.Column(db.Integer)
    geom = db.Column(Geometry(geometry_type='POINT', srid=2913))
    user_id = db.Column(db.Text)
    stop = db.Column(db.Integer, db.ForeignKey("stops.gid"), nullable=False)
    stop_key = orm.relationship("Stops", foreign_keys=stop)



    def __init__(self, date, rte, dir, geom, user_id, stop):
        self.date = date
        self.rte = rte
        self.dir = dir
        self.geom = geom
        self.user_id = user_id
        self.stop = stop

    def __repr__(self):
        return '<OnTemp: %r, %r, %r, %r >' %\
            (self.id, self.date, self.rte, self.dir)


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
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime)
    rte = db.Column(db.Integer)
    dir = db.Column(db.Integer)
    #NOTE see nots from fixme above Stops model
    on_stop = db.Column(db.Integer, db.ForeignKey("stops.gid"), nullable=False)
    off_stop = db.Column(db.Integer, db.ForeignKey("stops.gid"), nullable=False)
    on = orm.relationship("Stops", foreign_keys=on_stop)
    off = orm.relationship("Stops", foreign_keys=off_stop)
    user_id = db.Column(db.Text)


    def __init__(self, date, rte, dir, on_stop, off_stop, user_id):
        self.date = date
        self.rte = rte
        self.dir = dir
        self.on_stop = on_stop
        self.off_stop = off_stop
        self.user_id = user_id

    def __repr__(self):
        return '<OnOffPairs: id:%r, on_id:%r, off_id:%r >' %\
            (self.id, self.on_stop, self.off_stop)


class Users(db.Model):
    __tablename__ = 'users'
    username = db.Column(db.Text, primary_key=True)
    password_hash = db.Column(db.Text)

    def __init__(self, username, password_hash):
        self.username = username
        self.password_hash = password_hash

    def __repr__(self):
        return '<User: Name: %r %r, Username:%r >' %\
            (self.first, self.last, self.username)


class Stops(db.Model):
    __tablename__ = 'stops'
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

