import os, sys, json

from flask import Blueprint, redirect, url_for,render_template, jsonify, request
from sqlalchemy import func
from sqlalchemy.orm import aliased
from geoalchemy2 import functions as geofunc

from api import db
from ..shared.models import Stops, Routes, SurveysCore, SurveysLng


STATIC_DIR = '/long'
mod_long = Blueprint('long', __name__, url_prefix='/long')


def static(html, static=STATIC_DIR):
    """returns correct path to static directory"""
    return os.path.join(static, html)


@mod_long.route('/')
def index():
    return redirect(url_for('.map'))


def query_locations(uri):
    On = aliased(Stops)
    Off = aliased(Stops)

    query = db.session.query(
        SurveysCore.uri.label('uri'),
        SurveysCore.rte.label('rte'),
        SurveysCore.dir.label('dir'),
        func.ST_AsGeoJSON(func.ST_Transform(SurveysCore.orig_geom, 4326))
            .label('orig_geom'),
        func.ST_AsGeoJSON(func.ST_Transform(SurveysCore.dest_geom, 4326))
            .label('dest_geom'),
        func.ST_AsGeoJSON(func.ST_Transform(On.geom, 4326))
            .label('on_geom'),
        On.stop_name.label('on_stop'),
        func.ST_AsGeoJSON(func.ST_Transform(Off.geom, 4326))
            .label('off_geom'),
        Off.stop_name.label('off_stop'),
        SurveysCore.transfers_before.label('transfers_before'),
        SurveysCore.tb_1.label('tb_1'),
        SurveysCore.tb_2.label('tb_2'),
        SurveysCore.tb_3.label('tb_3'),
        SurveysCore.transfers_after.label('transfers_after'),
        SurveysCore.ta_1.label('ta_1'),
        SurveysCore.ta_2.label('ta_2'),
        SurveysCore.ta_3.label('ta_3'))\
        .join(On, SurveysCore.board).join(Off, SurveysCore.alight)\
        .filter(SurveysCore.uri == uri).first()

        
    
    points = None
    rte = None
    if (query and query.orig_geom and query.dest_geom 
        and query.on_geom and query.off_geom):
        
        #print query.rte
        #print query.dir
        line = db.session.query(
            func.ST_AsGeoJSON(func.ST_Transform(func.ST_Union(Routes.geom), 4326))\
            .label('geom')).filter(Routes.rte == query.rte)\
            .filter(Routes.dir == query.dir).all()

        if len(line) == 1:
            rte = json.loads(line[0].geom)

        points = {}
        points['orig'] = json.loads(query.orig_geom)
        points['dest'] = json.loads(query.dest_geom)
        points['on'] = {}
        points['on']['name'] = query.on_stop
        points['on']['geom'] = json.loads(query.on_geom)
        points['off'] = {}
        points['off']['name'] = query.off_stop
        points['off']['geom'] = json.loads(query.off_geom)

    return points, rte

@mod_long.route('/map')
def map():
    keys = []
    for uri in db.session.query(SurveysCore.uri.label('uri')):
        keys.append(uri.uri)
    
    return render_template(static('map.html'), keys=keys)


@mod_long.route('/_geoquery', methods=['GET'])
def geo_query():
    uri = request.args.get('uri')
    points, lines = query_locations(uri)
    return jsonify({'points':points, 'lines':lines})


def transfers(query):
    before = 0
    after = 0
    before_rte = []
    after_rte = []

    
    if query and query.transfers_before and query.transfers_after:
        before = int(query.transfers_before)
        after = int(query.transfers_after)

        if before > 0:
            before_rte.append(query.tb_1)
            if before > 1:
                before_rte.append(query.tb_2)
                if before > 2:
                    before_rte.append(query.tb_3)
        
        if after > 0:
            after_rte.append(query.ta_1)
            if after > 1:
                after_rte.append(query.ta_2)
                if after > 2:
                    after_rte.append(query.ta_3)
    
    rtes = []
    print "before"
    for rte in before_rte:
        print rte
        geom = db.session.query(
            func.ST_AsGeoJSON(func.ST_Transform(func.ST_Union(Routes.geom), 4326))
            .label('geom')).filter(Routes.rte == before_rte[0]).first()
        rtes.append(json.loads(geom.geom))
        #for g in geom:
        #    rtes.append(json.loads(g.geom))
    print "after"
    for rte in after_rte:
        print rte
        geom = db.session.query(
            func.ST_AsGeoJSON(func.ST_Transform(func.ST_Union(Routes.geom), 4326))
            .label('geom')).filter(Routes.rte == before_rte[0]).first()
        rtes.append(json.loads(geom.geom))
        #for g in geom:
        #    rtes.append(json.loads(g.geom))









