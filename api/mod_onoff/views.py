import os
import sys

from flask import Blueprint, redirect, url_for,render_template, jsonify, request
from sqlalchemy import func

from models import Scans, OnOffPairs_Scans, OnOffPairs_Stops
from helper import Helper
from api import app, db


STATIC_DIR = '/onoff'
#INBOUND = '1'
#OUTBOUND = '0'
#DIRECTION = {'1':'Inbound', '0':'Outbound'}
#TRAINS = ['190','193','194','200']


mod_onoff = Blueprint('onoff', __name__, url_prefix='/onoff')


def static(html, static=STATIC_DIR):
    """returns correct path to static directory"""
    return os.path.join(static, html)

@mod_onoff.route('/')
def index():
    return redirect(url_for('.status'))

@mod_onoff.route('/test')
def test():
    #Helper.summary_status_query()
    #quotas_file = os.path.join(app.config["ROOT_DIR"], "data/pmlr_targets.csv")
    #helper = Helper(quota_file=quotas_file)
    return ""

@mod_onoff.route('/overview')
def onoff_overview():
    #results = Count.complete()
    return ""#render_template(static('overview.html'), results=results)

@mod_onoff.route('/status')
def status():
    routes = [ route['rte_desc'] for route in Helper.get_routes() ]
    chart = Helper.summary_chart()

    return render_template(
        static('status.html'), routes=routes,chart=chart)


#@mod_onoff.route('/status/_details', methods=['GET'])
#def status_details():
#     targets = Helper.get_targets()
#     return jsonify(data=targets)



@mod_onoff.route('/status/_details', methods=['GET'])
def status_details():
     if 'rte_desc' in request.args.keys():
         app.logger.debug(request.args['rte_desc'])
         response = Helper.query_route(request.args['rte_desc'])

         #line = request.args.get('line')
         #response = Chart.single_route(line)
     else:
         pass
         #routes = Query.routes()
         #response = Chart.all_routes(routes)
     #app.logger.debug(response)
     
     return jsonify(response)


@mod_onoff.route('/map')
def map():
    return render_template(static('map.html'))


@mod_onoff.route('/data')
def data():
    """Sets up table headers and dropdowns in template"""
    headers = ['Date', 'Time', 'User', 'Route', 'Direction', 'On Stop', 'Off Stop']
    routes = [ route['rte_desc'] for route in Helper.get_routes() ]
    return render_template(static('data.html'), routes=routes, headers=headers)


@mod_onoff.route('/data/_query', methods=['GET'])
def data_query():
    #kwargs = {}
    #for key, value in request.args.iteritems():
    #    kwargs[key] = value
    #records = Query.records(**kwargs)
    return jsonify({})#{'records':records})




