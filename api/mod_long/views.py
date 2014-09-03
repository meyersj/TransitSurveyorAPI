import os
import sys
import json

from flask import Blueprint, redirect, url_for,render_template, jsonify, request
from sqlalchemy import func
from sqlalchemy.orm import aliased
from geoalchemy2 import functions as geofunc
#from geoalchemy2 import func


from models import Stops, SurveysCore, SurveysLng

from api import db


STATIC_DIR = '/long'
INBOUND = '1'
OUTBOUND = '0'
DIRECTION = {'1':'Inbound', '0':'Outbound'}
TRAINS = ['190','193','194','200']


mod_long = Blueprint('long', __name__, url_prefix='/long')


def static(html, static=STATIC_DIR):
    """returns correct path to static directory"""
    return os.path.join(static, html)


@mod_long.route('/')
def index():
    return redirect(url_for('.map'))

@mod_long.route('/map')
def map():
    On = aliased(Stops)
    Off = aliased(Stops)
    
    query = db.session.query(
        SurveysCore.uri.label('uri'),
        func.ST_AsGeoJSON(func.ST_Transform(SurveysCore.orig_geom, 4326))
            .label('orig_geom'),
        func.ST_AsGeoJSON(func.ST_Transform(SurveysCore.dest_geom, 4326))
            .label('dest_geom'),
        func.ST_AsGeoJSON(func.ST_Transform(On.geom, 4326))
            .label('on_geom'),
        On.stop_name.label('on_stop'),
        func.ST_AsGeoJSON(func.ST_Transform(Off.geom, 4326))
            .label('off_geom'),
        Off.stop_name.label('off_stop'))\
        .join(On, SurveysCore.board).join(Off, SurveysCore.alight).first()
    
    data = {}
    data['orig'] = json.loads(query.orig_geom)
    data['dest'] = json.loads(query.dest_geom)
    data['on'] = {}
    data['on']['name'] = query.on_stop
    data['on']['geom'] = json.loads(query.on_geom)
    data['off'] = {}
    data['off']['name'] = query.off_stop
    data['off']['geom'] = json.loads(query.off_geom)

    return render_template(static('map.html'), data=data)


