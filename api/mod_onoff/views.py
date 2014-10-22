import os
import sys

from flask import Blueprint, redirect, url_for,render_template, jsonify, request
from sqlalchemy import func

from models import Scans, OnOffPairs_Scans, OnOffPairs_Stops
from helper import Helper, Count, Chart, Query, summary_status_query
from api import app, db


STATIC_DIR = '/onoff'
INBOUND = '1'
OUTBOUND = '0'
DIRECTION = {'1':'Inbound', '0':'Outbound'}
TRAINS = ['190','193','194','200']


mod_onoff = Blueprint('onoff', __name__, url_prefix='/onoff')


def static(html, static=STATIC_DIR):
    """returns correct path to static directory"""
    return os.path.join(static, html)


@mod_onoff.route('/')
def index():
    #print url_for('onoff/overview')
    return redirect(url_for('.onoff_overview'))


@mod_onoff.route('/test')
def test():
     Helper.summary_status_query()
     #quotas_file = os.path.join(app.config["ROOT_DIR"], "data/pmlr_targets.csv")
     #helper = Helper(quota_file=quotas_file)
     return ""


@mod_onoff.route('/overview')
def onoff_overview():
    results = Count.complete()
    return render_template(static('overview.html'), results=results)


def sort_targets(targets):
    grouped = {}

    for stats in targets:
        rte = stats['rte']
        rte_desc = stats['rte_desc']

        data = {}
        data['target'] = stats['target']
        data['complete'] = stats['complete']
        data['dir_desc'] = stats['dir_desc']

        if rte not in grouped:
            grouped[rte] = {}
            grouped[rte]['rte_desc'] = stats['rte_desc']
            grouped[rte]['data'] = {} 
        grouped[rte]['data'][stats['dir']] = data
        
    sorted_rtes = sorted([int(key) for key in grouped.keys()])
    targets_list = []
    for rte in sorted_rtes:
        rte = str(rte)
        data = {
            'rte':rte,
            'rte_desc':grouped[rte]['rte_desc'],
            '0':grouped[rte]['data']['0'],
            '1':grouped[rte]['data']['1']
        }
        targets_list.append(data) 
    
    return targets_list


@mod_onoff.route('/status')
def status():
    helper = Helper()
    #count = Helper.get_count()
    #summary_status = Helper.summary_status_query()
    chart = Helper.summary_chart()
    print helper.routes
    
    #print chart
    #print helper.routes
    #print summary_status
    # convert all route numbers to integer
    # sort list then convert route numbers
    # back to strings
    #routes = [ int(rte) for rte in helper.routes ]
    #routes = [ str(rte) for rte in sorted(set(route)) ]

    #targets = sort_targets(helper.targets)

    return render_template(
        static('status.html'), routes=helper.routes,
        chart=chart
    )


@mod_onoff.route('/status/_details', methods=['GET'])
def status_details():
     helper = Helper()
     return jsonify(data=helper.targets)


"""
@mod_onoff.route('/status/_details', methods=['GET'])
def status_details():
     if 'line' in request.args.keys():
         line = request.args.get('line')
         response = Chart.single_route(line)
     else:
         routes = Query.routes()
         response = Chart.all_routes(routes)
     app.logger.debug(response)
     
     return jsonify(**response)
"""

@mod_onoff.route('/map')
def map():
    return render_template(static('map.html'))


@mod_onoff.route('/data')
def data():
    """Sets up table headers and dropdowns in template"""
    headers = ['Date', 'Time', 'User', 'Route', 'Direction', 'On Stop', 'Off Stop']
    routes = Query.routes()
    return render_template(static('data.html'), routes=routes, headers=headers)


@mod_onoff.route('/data/_query', methods=['GET'])
def data_query():
    kwargs = {}
    for key, value in request.args.iteritems():
        kwargs[key] = value
    records = Query.records(**kwargs)
    return jsonify({'records':records})




