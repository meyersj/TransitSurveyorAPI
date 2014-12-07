import os
import sys
import time

from flask import make_response, Blueprint, redirect
from flask import url_for,render_template, jsonify, request
from sqlalchemy import func

from models import Scans, OnOffPairs_Scans, OnOffPairs_Stops
from helper import Helper
from api import app, db
from api import debug, error, Session #web_session

STATIC_DIR = '/onoff'
mod_onoff = Blueprint('onoff', __name__, url_prefix='/onoff')


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

"""

@mod_onoff.route('/old_status')
def status():
    routes = [ route['rte_desc'] for route in Helper.get_routes() ]
    chart = Helper.summary_chart()
    #streetcar = {"Portland Streetcar - NS Line":{"target
    return render_template(
        static('status.html'), routes=routes,chart=chart)
"""

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


