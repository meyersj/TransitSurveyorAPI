import os
import sys

from flask import Blueprint, redirect, url_for,render_template, jsonify, request
from sqlalchemy import func

from models import Scans, OnOffPairs_Scans, OnOffPairs_Stops
from helper import Helper
from api import app, db
from api import debug, error, web_session

STATIC_DIR = '/onoff'
mod_onoff = Blueprint('onoff', __name__, url_prefix='/onoff')


def static(html, static=STATIC_DIR):
    """returns correct path to static directory"""
    return os.path.join(static, html)

@mod_onoff.route('/')
def index():
    return redirect(url_for('.overview'))

@mod_onoff.route('/test')
def test():
    return "hilogg"

"""
@mod_onoff.route('/overview')
def overview():
    #results = Count.complete()
    return render_template(static('base.html'))
    #return "overview"#render_template(static('overview.html'), results=results)
"""

@mod_onoff.route('/table_status')
def overview():
    routes = [ route['rte_desc'] for route in Helper.get_routes() ]
    data = Helper.query_route_status()
    query = web_session.execute("""
        SELECT rte_desc, sum(count) AS count
        FROM v.records
        WHERE rte_desc LIKE 'Portland Streetcar%'
        GROUP by rte_desc;""")
    
    streetcar = {
            "Portland Streetcar - NS Line":{'target':2182, 'count':0},
            "Portland Streetcar - CL Line":{'target':766, 'count':0}
    }
    
    for record in query:
        debug(record)
        streetcar[record[0]]['count'] = int(record[1])
    
    return render_template(static('table_status.html'), 
            streetcar=streetcar, routes=routes, data=data)


@mod_onoff.route('/status')
def status():
    routes = [ route['rte_desc'] for route in Helper.get_routes() ]
    chart = Helper.summary_chart()
    #streetcar = {"Portland Streetcar - NS Line":{"target
    return render_template(
        static('status.html'), routes=routes,chart=chart)

#@mod_onoff.route('/status/_details', methods=['GET'])
#def status_details():
#     targets = Helper.get_targets()
#     return jsonify(data=targets)



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

#@mod_onoff.route('/map')
#def map():
#    return render_template(static('map.html'))

@mod_onoff.route('/data')
def data():
    """Sets up table headers and dropdowns in template"""
    headers = ['Date', 'Time', 'User', 'Route', 'Direction', 'On Stop', 'Off Stop']
    routes = [ route['rte_desc'] for route in Helper.get_routes() ]
    
    directions = Helper.get_directions()

    # build response
    #for direction in directions:
    #directions = [ direction['dir_desc'] for direction in Helper.get_directions() ]

    return render_template(static('data.html'),
            routes=routes, directions=directions, headers=headers)


@mod_onoff.route('/data/_query', methods=['GET'])
def data_query():
    response = []
    rte_desc = ""
    dir_desc = ""

    if 'rte_desc' in request.args.keys():
        rte_desc = request.args['rte_desc'].strip()
    if 'dir_desc' in request.args.keys():
        dir_desc = request.args['dir_desc'].strip()
        debug("dir desc: " + dir_desc)

    response = Helper.query_route_data(rte_desc=rte_desc, dir_desc=dir_desc)
        
    return jsonify(data=response)




