import os
import sys
import time
import json
from decimal import Decimal

from flask import make_response, Blueprint, redirect
from flask import url_for,render_template, jsonify, request
from sqlalchemy import func

from models import Scans, OnOffPairs_Scans, OnOffPairs_Stops
from helper import Helper
from spatial import Spatial
from api import app, db
from api import debug, error, Session
from ..shared.helper import Helper as h

STATIC_DIR = '/onoff'
mod_onoff = Blueprint('onoff', __name__, url_prefix='/onoff', static_folder='static')


def static(html, static=STATIC_DIR):
    """returns correct path to static directory"""
    return os.path.join(static, html)

@mod_onoff.route('/')
def index():
    return redirect(url_for('.surveyor_status'))

"""
@mod_onoff.route('/test')
def test():
    return "hilogg"
"""
@mod_onoff.route('/overview')
def overview():
    return render_template(static('base.html'))

@mod_onoff.route('/status')
def status():
    routes = [ route['rte_desc'] for route in Helper.get_routes() ]
    data = Helper.query_route_status()
    web_session = Session()
    query = web_session.execute("""
        SELECT rte_desc, sum(count) AS count
        FROM v.records
        WHERE rte_desc LIKE 'Portland Streetcar%'
        GROUP by rte_desc;""")
    
    # hardcode streetcar targets, then populate the count
    streetcar = {
            "Portland Streetcar - NS Line":{'target':2182, 'count':0},
            "Portland Streetcar - CL Line":{'target':766, 'count':0}
    }
    for record in query:
        debug(record)
        streetcar[record[0]]['count'] = int(record[1])
    web_session.close()
   
    summary = Helper.query_routes_summary()
    debug(summary) 
    return render_template(static('status.html'), 
            streetcar=streetcar, routes=routes, data=data, summary=summary)


@mod_onoff.route('/status/_details', methods=['GET'])
def status_details():
     response = {'success':False}
     
     if 'rte_desc' in request.args.keys():
         data = Helper.query_route_status(rte_desc=request.args['rte_desc'])
         chart = Helper.single_chart(data)
         response['success'] = True
         response['data'] = data
         response['chart'] = chart
     
     return jsonify(response)


@mod_onoff.route('/data')
def data():
    """Sets up table headers and dropdowns in template"""
    headers = ['Date', 'Time', 'User', 'Route', 'Direction', 'On Stop', 'Off Stop']
    routes = [ route['rte_desc'] for route in Helper.get_routes() ]
    directions = Helper.get_directions()
    users = Helper.get_users()
    
    return render_template(static('data.html'),
            routes=routes, directions=directions, headers=headers,
            users=users)


@mod_onoff.route('/data/_query', methods=['GET'])
def data_query():
    response = []
    user = ""
    rte_desc = ""
    dir_desc = ""
    csv = False

    if 'rte_desc' in request.args.keys():
        rte_desc = request.args['rte_desc'].strip()
    if 'dir_desc' in request.args.keys():
        dir_desc = request.args['dir_desc'].strip()
    if 'user' in request.args.keys():
        user = request.args['user'].strip()
        debug(user)
    if 'csv' in request.args.keys():
        csv = request.args['csv']

    if csv:
        data = Helper.query_route_data(
            user=user, rte_desc=rte_desc, dir_desc=dir_desc,csv=csv
        )
        response = ""
        # build csv string
        for record in data:
            response += ','.join(record) + '\n'
    else:
        response = Helper.query_route_data(
            user=user, rte_desc=rte_desc, dir_desc=dir_desc
        )

    return jsonify(data=response)


@mod_onoff.route('/surveyors')
def surveyor_status():
    return render_template(static('surveyors.html'))


@mod_onoff.route('/surveyors/_summary', methods=['GET'])
def surveyor_summary_query():
    response = []
    date = time.strftime("%d-%m-%Y")

    if 'date' in request.args.keys():
        date = request.args['date'].strip()

    response = Helper.current_users(date)
    debug(response)
    return jsonify(users=response)

@mod_onoff.route('/map')
def map():
    routes = [ route['rte_desc'] for route in h.get_routes() ]
    directions = h.get_directions()
    return render_template(static('map.html'),
        routes=routes, directions=directions
    )



@mod_onoff.route('/map/_details', methods=['GET'])
def map_details():
    response = {'success':False}
    if 'rte_desc' in request.args.keys():
        rte_desc = request.args['rte_desc'].strip()
        rte = h.rte_lookup(rte_desc)
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
        query_routes = session.execute("""
            SELECT dir, ST_AsGeoJson(ST_Transform(ST_Union(geom), 4326))
            FROM tm_routes
            WHERE rte = :rte
            GROUP BY dir;""", {'rte':rte})
        query_minmax = session.execute("""
            SELECT dir, label, stop_name, ST_AsGeoJson(ST_Transform(geom, 4326))
            FROM long.stop_minmax
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
                return False

        data = {}
        data[0] = []
        data[1] = []
        time_data = {}
        time_data[0] = {}
        time_data[1] = {}
        routes_geom = {}
        minmax = {} 
        for record in query:
            data[record[0]].append(build_data(record))
        for record in query_time:
            tad = record[1]
            if tad not in time_data[record[0]]:
                time_data[record[0]][tad] = []
            ons = int_zero(record[4])
            count = int_zero(record[5])
            bucket = int_zero(record[6])
            time_data[record[0]][tad].insert(bucket, {"count":count, "ons":ons})
        for record in query_routes:
            routes_geom[record[0]] = {
                'dir':record[0],
                'geom':json.loads(record[1])
            }
        for record in query_minmax:
            if record[0] not in minmax:
                minmax[record[0]] = {}
            minmax[record[0]][record[1]] = {
                'geom':record[3],
                'stop_name':record[2]
            }
        response['success'] = True
        response['data'] = data
        response['time_data'] = time_data
        response['routes'] = routes_geom
        response['minmax'] = minmax
        session.close()
    return jsonify(response)


@mod_onoff.route('/map_offs')
def map_offs():
    routes = [ {
        'rte':route['rte'], 'rte_desc':route['rte_desc']
        } for route in h.get_routes() ]
    directions = h.get_directions()
    return render_template(static('map_offs.html'),
        routes=routes, directions=directions
    )

@mod_onoff.route('/map_offs/_details', methods=['GET'])
def map_offs_details():
    response = {'success':False}
    if 'rte_desc' in request.args.keys():
        rte_desc = request.args['rte_desc'].strip()
        rte = h.rte_lookup(rte_desc)
        session = Session()
        fields = ['dir', 'tad', 'centroid', 'stops', 'ons', 'count']
        query_time = session.execute("""
            SELECT """ + ','.join(fields) + """, bucket
            FROM long.tad_time_stats
            WHERE rte = :rte;""", {'rte':rte})
        query_markers = session.execute("""
            SELECT dir, tad, centroid, stops, ons, count
            FROM long.tad_stats
            WHERE rte = :rte;""", {'rte':rte})
        query_tads = session.execute("""
            SELECT
                r.dir,
                t.tadce10 AS tad,
                ST_AsGeoJson(ST_Transform(ST_Union(t.geom), 4326)) AS geom,
                ST_AsGeoJson(ST_Transform(ST_Centroid(ST_Union(t.geom)), 4326)) AS centroid
            FROM tad AS t
            JOIN tm_routes AS r
            ON ST_Intersects(t.geom, r.geom)
            WHERE r.rte = :rte
            GROUP BY r.dir, t.tadce10;""", {'rte':rte})
        query_data_summary = session.execute("""
            SELECT
                dir,
                on_tad,
                sum(count) AS ons
            FROM long.tad_onoff
            WHERE rte = :rte
            GROUP BY dir, on_tad;""", {'rte':rte})
        query_data = session.execute("""
            SELECT
                dir,
                on_tad,
                off_tad,
                count
            FROM long.tad_onoff
            WHERE rte = :rte;""", {'rte':rte})
        query_routes = session.execute("""
            SELECT dir, ST_AsGeoJson(ST_Transform(ST_Union(geom), 4326))
            FROM tm_routes
            WHERE rte = :rte
            GROUP BY dir;""", {'rte':rte})
        query_minmax = session.execute("""
            SELECT dir, label, stop_name, ST_AsGeoJson(ST_Transform(geom, 4326))
            FROM long.stop_minmax
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

        tads = []
        stops = {}
        stops[0] = {}
        stops[1] = {}
        summary = {}
        summary[0] = []
        summary[1] = []
        data = {}
        data[0] = {}
        data[1] = {}
        routes_geom = {}
        minmax = {} 
        time_data = {}
        time_data[0] = {}
        time_data[1] = {}
      
        for record in query_tads:
            dir_ = record[0]
            tad = record[1]
            geom = record[2]
            centroid = record[3]
            tads.append({'dir':dir_, 'tad':tad, 'geom':geom, 'centroid':centroid})
        for record in query_markers:
            dir_ = record[0]
            tad = record[1]
            centroid = json.loads(record[2])
            stops_geom = json.loads(record[3])
            ons = int_zero(record[4])
            count = int_zero(record[5])
            stops[dir_][tad] = {
                'tad':tad, 'centroid':centroid, 'count':count, 'stops':stops_geom, 'ons':ons
            }
        for record in query_data_summary:
            dir_ = record[0]
            tad_on = record[1]
            ons = int(record[2])
            summary[dir_].append({'tad':tad_on, 'ons':ons})
        for record in query_data:
            dir_ = record[0]
            tad_on = record[1]
            tad_off = record[2]
            offs = int(record[3])
            if tad_on not in data[dir_]:
                data[dir_][tad_on] = {}
                data[dir_][tad_on]['offs'] = []
            data[dir_][tad_on]['offs'].append({'tad':tad_off, 'offs':offs})
        for record in query_routes:
            routes_geom[record[0]] = {
                'dir':record[0],
                'geom':json.loads(record[1])
            }
        for record in query_minmax:
            if record[0] not in minmax:
                minmax[record[0]] = {}
            minmax[record[0]][record[1]] = {
                'geom':record[3],
                'stop_name':record[2]
            }
        for record in query_time:
            tad = record[1]
            if tad not in time_data[record[0]]:
                time_data[record[0]][tad] = []
            ons = int_zero(record[4])
            count = int_zero(record[5])
            bucket = int_zero(record[6])
            time_data[record[0]][tad].insert(bucket, {"count":count, "ons":ons})

        response['success'] = True
        response['stops'] = stops
        response['summary'] = summary
        response['data'] = data
        response['tads'] = tads
        response['routes'] = routes_geom
        response['minmax'] = minmax
        response['time_data'] = time_data
        
        session.close()
    return jsonify(response)


