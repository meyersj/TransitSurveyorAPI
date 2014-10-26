import csv, os

from sqlalchemy import func, desc, distinct, cast, Integer

from flask import current_app
from api.shared.models import Quotas, Scans, OnOffPairs_Scans, OnOffPairs_Stops
from api import db

app = current_app

GREEN_STATUS = '#76DB55'
RED_STATUS = '#DB5555'
INBOUND = '1'
OUTBOUND = '0'
DIRECTION = {'1':'Inbound', '0':'Outbound'}
TRAINS = ['190','193','194','200']

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
        
        counts = {}
        for record in scans_status.union(stops_status):
            counts[record.rte] = record.count 

        quotas = db.session.query(
            cast(Quotas.rte, Integer).label('rte'),
            Quotas.rte_desc.label('rte_desc'),
            func.sum(Quotas.onoff_target).label('target')
        ).group_by(Quotas.rte, Quotas.rte_desc).order_by('rte')
       
        status = []
        for quota in quotas:
            data = {}
            data['rte'] = str(quota.rte)
            data['rte_desc'] = quota.rte_desc
            data['target'] = int(quota.target)
            if quota.rte in counts: data['count'] = counts[quota.rte]
            else: data['count'] = 0
            status.append(data)
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
    def single_chart(data):
        app.logger.debug(data)
        
        categories = []
        remaining = []
        complete = []

        categories.append(data['0']['dir_desc'])
        categories.append(data['1']['dir_desc'])
        categories.append('Total')

        count_total = 0
        target_total = 0
        for i in ['0', '1']:
            count = float(data[i]['count'])
            count_total += count
            target = float(data[i]['target'])
            target_total += target
            pct = round( (count / target) * 100.0 )
            remaining.append(100 - pct)
            complete.append(pct)
       
        pct_total = round( (count_total / target_total) * 100.0 )
        remaining.append(100 - pct_total)
        complete.append(pct_total)

        series = [
            {'data':remaining, 'name':'remaining', 'color':RED_STATUS},
            {'data':complete, 'name':'complete', 'color':GREEN_STATUS}
        ]
        
        return {'series':series, 'categories':categories}




    @staticmethod
    def get_targets():
        query = db.session.query(Quotas)
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
            cast(Quotas.rte, Integer).label('rte'),
            Quotas.rte_desc.label('rte_desc'))\
            .distinct().order_by('rte')

        ret_val = [ {'rte':str(route.rte), 'rte_desc':route.rte_desc}
            for route in routes ]
        return ret_val

    @staticmethod
    def query_route_data(rte_desc):
        response = []
        rte = db.session.query(Quotas.rte)\
                .filter(Quotas.rte_desc == rte_desc).first().rte
        app.logger.debug(rte)
        
        if rte in TRAINS:
            data = db.session.query(OnOffPairs_Stops)\
                .filter(OnOffPairs_Stops.line == rte)\
                .order_by(OnOffPairs_Stops.date.desc())\
                .limit(100).all()
           
            if data:
                for d in data:
                    r = {}
                    r['date'] = str(d.date.date())
                    r['time'] = str(d.date.time())
                    r['user_id'] = d.user_id
                    r['rte_desc'] = d.on.rte_desc
                    r['dir_desc'] = d.on.dir_desc
                    r['on_stop'] = d.on.stop_name
                    r['off_stop'] = d.off.stop_name
                    response.append(r)
        else:
            data = db.session.query(OnOffPairs_Scans)\
                .join(OnOffPairs_Scans.on)\
                .filter_by(line = rte)\
                .order_by(Scans.date.desc())\
                .limit(100).all()
            
            if data:
                for d in data:
                    r = {}
                    r['date'] = str(d.on.date.date())
                    r['time'] = str(d.on.date.time()) + '/' + str(d.off.date.time())
                    r['user_id'] = d.on.user_id + '/' + d.off.user_id
                    r['rte_desc'] = d.on.stop_key.rte_desc
                    r['dir_desc'] = d.on.stop_key.dir_desc
                    r['on_stop'] = d.on.stop_key.stop_name
                    r['off_stop'] = d.off.stop_key.stop_name
                    response.append(r)
            
        print response
        return response
    
    @staticmethod
    def query_route_status(rte_desc):
        quotas = db.session.query(
            cast(Quotas.rte, Integer).label('rte'),
            Quotas.rte_desc.label('rte_desc'),
            Quotas.dir.label('dir'),
            Quotas.dir_desc.label('dir_desc'),
            func.sum(Quotas.onoff_target).label('target')
        ).filter(Quotas.rte_desc==rte_desc)\
        .group_by(Quotas.rte, Quotas.rte_desc, Quotas.dir, Quotas.dir_desc).order_by('rte')

        rte = str(quotas[0].rte)
        targets = {}
        for r in quotas:
            data = {}
            data['dir_desc'] = r.dir_desc
            data['target'] = int(r.target)
            targets[r.dir] = data
        
        if rte in TRAINS:
            status = db.session.query(
                cast(OnOffPairs_Stops.line, Integer).label('rte'),
                OnOffPairs_Stops.dir.label('dir'),
                func.count(OnOffPairs_Stops.id).label('count')
            ).filter(OnOffPairs_Stops.line == rte)\
            .group_by(OnOffPairs_Stops.line, OnOffPairs_Stops.dir)

        else:
            status = db.session.query(
                cast(Scans.line, Integer).label('rte'),
                Scans.dir.label('dir'),
                func.count(Scans.id).label('count')
            ).join(OnOffPairs_Scans.on)\
            .filter(Scans.line == rte).group_by(Scans.line, Scans.dir)
       
        response = {}
        response['rte_desc'] = rte_desc

        if status.count() > 0:
            for s in status:
                response[s.dir] = targets[s.dir]
                response[s.dir]['count'] = int(s.count)
        else:
            response['0'] = targets['0']
            response['0']['count'] = 0
            response['1'] = targets['1']
            response['1']['count'] = 0

        return response


