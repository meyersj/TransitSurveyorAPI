import os
import sys

from flask import Blueprint, redirect, url_for,render_template, jsonify, request
from sqlalchemy import func

from models import Scans, OnOffPairs_Scans, OnOffPairs_Stops
from helper import Count, Chart, Query
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


@mod_onoff.route('/overview')
def onoff_overview():
    results = Count.complete()
    return render_template(static('overview.html'), results=results)


@mod_onoff.route('/status')
def status():
    routes = Query.routes()
    app.logger.debug(routes)
    return render_template(static('status.html'), routes=routes)


@mod_onoff.route('/status/_details', methods=['GET'])
def status_details():
     if 'line' in request.args.keys():
         line = request.args.get('line')
         response = Chart.single_route(line)
     else:
         routes = Query.routes()
         response = Chart.all_routes(routes)
     return jsonify(**response)


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




