import csv, os

from sqlalchemy import func, desc, distinct, cast, Integer

from flask import current_app

from models import Quotas as QuotasT, Scans, OnOffPairs_Scans, OnOffPairs_Stops
from api import db, app


GREEN_STATUS = '#76DB55'
RED_STATUS = '#DB5555'
INBOUND = '1'
OUTBOUND = '0'
DIRECTION = {'1':'Inbound', '0':'Outbound'}
TRAINS = ['190','193','194','200']

# return total number of records for each route being surveyed
def summary_status_query():
    stops_status = db.session.query(
        cast(OnOffPairs_Stops.line, Integer).label('rte'),
        func.count(OnOffPairs_Stops.id).label('count')
    ).group_by(OnOffPairs_Stops.line)
    
    scans_status = db.session.query(
        cast(Scans.line, Integer).label('rte'),
        func.count(Scans.id).label('count')
    ).join(OnOffPairs_Scans.on).group_by(Scans.line)
    
    # create ordered ordered list of dictories
    status = [ 
        {'rte':str(record.rte), 'count':int(record.count) } 
        for record in scans_status.union(stops_status).order_by('rte')
    ]
    return status

class Helper(object):
    targets = None
    routes = None

    def __init__(self, quota_file=None):
        #self.targets = self.get_targets()
        self.routes = self.get_routes()

    @staticmethod
    def get_count(**kwargs):
        count = 0
        
        count += db.session.query(OnOffPairs_Stops)\
            .filter_by(**kwargs)\
            .count()
            #else:
        
        count += db.session.query(OnOffPairs_Scans)\
            .join(OnOffPairs_Scans.on)\
            .filter_by(**kwargs)\
            .count()
        return count

    # return total number of records for each route being surveyed
    @staticmethod
    def summary_status_query():
        stops_status = db.session.query(
            cast(OnOffPairs_Stops.line, Integer).label('rte'),
            func.count(OnOffPairs_Stops.id).label('count')
        ).group_by(OnOffPairs_Stops.line)
        
        scans_status = db.session.query(
            cast(Scans.line, Integer).label('rte'),
            func.count(Scans.id).label('count')
        ).join(OnOffPairs_Scans.on).group_by(Scans.line)

        # create ordered ordered list of dictories
        quotas = db.session.query(
            QuotasT.rte.label('rte'),
            QuotasT.rte_desc.label('rte_desc'),
            func.sum(QuotasT.onoff_target).label('target')
        ).group_by(QuotasT.rte, QuotasT.rte_desc)

        targets = {}  
        for target in quotas:
            rte = int(target.rte)
            targets[rte] = {}
            targets[rte]['rte_desc'] = str(target.rte_desc)
            targets[rte]['target'] = int(target.target)

        status = [ 
            {'rte':str(record.rte),
            'rte_desc':targets[record.rte]['rte_desc'],
            'count':int(record.count),
            'target':targets[record.rte]['target']}
            for record in scans_status.union(stops_status).order_by('rte')
        ]
        
        return status

    @staticmethod
    def summary_chart():
        status = Helper.summary_status_query() 
        
        categories = []
        remaining = []
        complete = []
        
        for record in status:
            pct = round((float(record['count']) / float(record['target'])) * 100)
            categories.append(record['rte_desc'])
            remaining.append(100 - pct)
            complete.append(pct)

        series = [
            {'data':remaining, 'name':'remaining', 'color':RED_STATUS},
            {'data':complete, 'name':'complete', 'color':GREEN_STATUS}
        ]
        
        return {'series':series, 'categories':categories}


    @staticmethod
    def get_targets():
        query = db.session.query(QuotasT)
        ret_val = []
        total = 0
        for row in query:            
            count = Helper.get_count(line=row.rte, dir=row.dir)
            total += count
            data = {
                'rte':row.rte,
                'dir':row.dir,
                'rte_desc':row.rte_desc,
                'dir_desc':row.dir_desc,
                'target':row.onoff_target,
                'complete':int(count)
            }
            ret_val.append(data) 
        return ret_val

    @staticmethod
    def get_routes():
        routes = db.session.query(
            cast(QuotasT.rte, Integer).label('rte'),
            QuotasT.rte_desc.label('rte_desc'))\
            .distinct().order_by('rte')

        ret_val = [ {'rte':str(route.rte), 'rte_desc':route.rte_desc}
            for route in routes ]
        return ret_val
 
    @staticmethod
    def query_route(rte_desc):
        targets = Helper.get_targets()
        response = {}
        for target in targets:
            if target['rte_desc'] == rte_desc:
                response[target['dir']] = {
                    'dir_desc':target['dir_desc'],
                    'target':target['target'],
                    'complete':target['complete']
                }

        return response


