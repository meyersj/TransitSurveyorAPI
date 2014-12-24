import os, sys, json

from flask import Blueprint, redirect, url_for,render_template, jsonify, request
from sqlalchemy import func
from sqlalchemy.orm import aliased
from geoalchemy2 import functions as geofunc

from api import db
from api import Session
from api import debug

from ..shared.models import Stops, Routes, SurveysCore, SurveysFlag
from ..shared.helper import Helper


from decimal import Decimal


STATIC_DIR = '/long'
mod_long = Blueprint('long', __name__, url_prefix='/long')


def static(html, static=STATIC_DIR):
    """returns correct path to static directory"""
    return os.path.join(static, html)


@mod_long.route('/')
def index():
    return redirect(url_for('.map'))

def query_locations(uri):
    ret_val = {}
    On = aliased(Stops)
    Off = aliased(Stops)
    session = Session()
    record = session.query(
        SurveysCore.uri,
        func.ST_AsGeoJSON(func.ST_Transform(SurveysCore.orig_geom, 4326))
            .label('orig_geom'),
        func.ST_AsGeoJSON(func.ST_Transform(SurveysCore.dest_geom, 4326))
            .label('dest_geom'),
        func.ST_AsGeoJSON(func.ST_Transform(On.geom, 4326))
            .label('on_geom'),
        func.ST_AsGeoJSON(func.ST_Transform(Off.geom, 4326))
            .label('off_geom'))\
        .join(On, SurveysCore.board).join(Off, SurveysCore.alight)\
        .filter(SurveysCore.uri == uri).first()
    if record:
        ret_val["orig_geom"] = json.loads(record.orig_geom)
        ret_val["dest_geom"] = json.loads(record.dest_geom)
        ret_val["on_geom"] = json.loads(record.on_geom)
        ret_val["off_geom"] = json.loads(record.off_geom)
    return ret_val
    

def check_flags(record):
    if not record.flags.english:
        return False
    if not record.flags.locations:
        return False
    return True


"""
Filter by route and direction
Show each tad centroid as pie chart with pct complete
"""
@mod_long.route('/map')
def map():
    session = Session()
    keys = []
    query = session.query(SurveysCore)
    for record in query:
        #TODO check that survey has not already been flagged by user
        if record.flags.locations:
            keys.append(record.uri)
    session.close()
    return render_template(static('map.html'), keys=keys)


@mod_long.route('/_geoquery', methods=['GET'])
def geo_query():
    points,lines = None, None
    if 'uri' in request.args:
        uri = request.args.get('uri')
        data = query_locations(uri)
        debug(data)
    return jsonify({'data':data})
    #return jsonify({'points':points, 'lines':lines})


@mod_long.route('/map2')
def map2():
    routes = [ route['rte_desc'] for route in Helper.get_routes() ]
    directions = Helper.get_directions()
    return render_template(static('map2.html'), routes=routes, directions=directions)

@mod_long.route('/map2/_details', methods=['GET'])
def map2_details():
    response = {'success':False}
    if 'rte_desc' in request.args.keys():
        rte_desc = request.args['rte_desc'].strip()
        rte = Helper.rte_lookup(rte_desc)
        session = Session()
        fields = ['dir', 'tad', 'centroid', 'stops', 'ons', 'count']
        query = session.execute("""
            SELECT """ + ','.join(fields) + """
            FROM long.tad_stats
            WHERE rte = :rte;""", {'rte':rte})

        query_time = session.execute("""
            SELECT """ + ','.join(fields) + """, bucket
            FROM long.tad_time_stats
            WHERE rte = :rte;""", {'rte':rte})
    
        def build_data(record):
            data = {}
            for index in range(1, len(fields)):
                field = record[index]
                if isinstance(field, Decimal): field = int(field)
                data[fields[index]] = field
            return data
        
        def int_zero(value):
            try:
                return int(value)
            except:
                return 0

        data = {}
        data[0] = []
        data[1] = []
        for record in query:
            data[record[0]].append(build_data(record))
        time_data = {}
        time_data[0] = {}
        time_data[1] = {}
        for record in query_time:
            #debug(record)
            tad = record[1]
            if tad not in time_data[record[0]]:
                time_data[record[0]][tad] = []
            ons = int_zero(record[4])
            count = int_zero(record[5])
            bucket = int_zero(record[6])
            #debug(time_data[record[0]][tad])
            time_data[record[0]][tad].insert(bucket, {"count":count, "ons":ons})
        response['success'] = True
        response['data'] = data
        response['time_data'] = time_data 
    return jsonify(response)






"""
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

"""







