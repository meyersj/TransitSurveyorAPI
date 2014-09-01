import csv, os

from sqlalchemy import func, desc

from models import Scans, OnOffPairs_Scans, OnOffPairs_Stops
from api import db


GREEN_STATUS = '#76DB55'
RED_STATUS = '#DB5555'
INBOUND = '1'
OUTBOUND = '0'
DIRECTION = {'1':'Inbound', '0':'Outbound'}
TRAINS = ['190','193','194','200']
QUOTAS = 'data/route_quotas.csv'
"""
QUOTA = {
    '9':100,
    '17':100,
    '19':100,
    '28':100,
    '29':100,
    '30':100,
    '31':100,
    '32':100,
    '33':100,
    '34':100,
    '35':100,
    '70':100,
    '75':100,
    '99':100,
    '152':100,
    '190':100,
    '193':100,
    '194':100,
    '200':100}
"""


def quota(quotas_csv, route, target):
    data = {}
    with open(quotas_csv, 'rb') as csv_file:
        rows = csv.DictReader(csv_file)
        for row in rows:
            #if row[target] != '0':
            data[row[route]] = int(row[target]) 
        return data


class Quota(object):

    @staticmethod
    def onoff(quotas_csv):
        print os.getcwd()
        
        return quota(quotas_csv, 'route_num', 'onoff_target')

    @staticmethod
    def long(quotas_csv):
        return quota(quotas_csv, 'route_num', 'long_target')


def percent(amount, total):
    if total == 0:
        return 100
    else:
        return round((float(amount) / total) * 100, 1)


class Count(object):

    @staticmethod
    def records(**kwargs):
        """Must have key 'line' in kwargs"""
        count = None
        if kwargs['line'] in TRAINS:
            count = db.session.query(OnOffPairs_Stops)\
                .filter_by(**kwargs)\
                .count()
        else:
            count = db.session.query(OnOffPairs_Scans)\
                .join(OnOffPairs_Scans.on)\
                .filter_by(**kwargs)\
                .count()
        return count

    @staticmethod
    def complete():
        routes = Query.routes()
        print routes
        
        complete = 0
        rem_count = 0
        rem_total = 0
        results = {}

        quotas = Quota.onoff(QUOTAS)

        for route in routes:
            data = {}
            count = Count.records(line=route)
            quota = quotas[str(route)]

            if count >= quota:
                complete += 1
            else:
                rem_count += count
                rem_total += quota
        
        results['complete'] = {'count':complete, 'rem':len(routes) - complete}
        results['remaining'] = {'count':rem_count, 'rem':rem_total - rem_count}

        return results

class Chart(object):

    @staticmethod
    def single_route(line):
        quotas = Quota.onoff(QUOTAS)

        
        in_total = quotas[str(line)]
        in_count = Count.records(line=line, dir=INBOUND)
        out_total = quotas[str(line)]
        out_count = Count.records(line=line, dir=OUTBOUND)
        #in_pct = percent(Count.records(line=line, dir=INBOUND), quotas[str(line)])
        #out_pct = percent(Count.records(line=line, dir=OUTBOUND), quotas[str(line)])
        categories = ['Inbound', 'Outbound']
        series =  [
            {'data':[in_total, out_total], 'name':'Remaining','color':RED_STATUS},
            {'data':[in_count, out_count], 'name':'Complete', 'color':GREEN_STATUS}]
        return {'series':series, 'categories':categories}

    @staticmethod
    def all_routes(routes):
        complete = []
    
        quotas = Quota.onoff(QUOTAS)
        
        for route in routes:
            #TODO fetch total from table instead of hard coded
            pct = percent(Count.records(line=route), quotas[str(route)] * 2)
            complete.append(pct)

        categories = ['Route ' + str(route) for route in routes]
        series = [
            {'data': [100 - pct for pct in complete],'name':'Remaining', 'color':RED_STATUS},
            {'data': complete,'name':'Complete', 'color':GREEN_STATUS}]
        return {'series':series, 'categories':categories}



TIME = "%H:%M"
DATE = "%m-%d-%y"

def date_time(on_date, off_date):
    date = on_date.strftime(DATE)
    time = on_date.strftime(TIME) + '-' + off_date.strftime(TIME)
    return date, time

class Query(object):
    
    @staticmethod
    def records(**kwargs):
        rows = []
        
        # fetch bus records
        records = db.session.query(OnOffPairs_Scans)\
            .join(OnOffPairs_Scans.off).filter_by(**kwargs)\
            .order_by(desc(Scans.date), "line", "dir")\
            .all()
        
        for r in records:
            line = r.on.line
            dir = r.on.dir
            on_stop = r.on.stop_key.stop_name
            off_stop = r.off.stop_key.stop_name
            date, time = date_time(r.on.date, r.off.date)
            user =  r.on.user_id + '/' + r.off.user_id
            rows.append(
                {'date':date,
                 'time':time,
                 'user':user,
                 'line': line,
                 'dir': DIRECTION[str(dir)],
                 'on': on_stop,
                 'off': off_stop})


        # fetch train records 
        records = db.session.query(OnOffPairs_Stops).filter_by(**kwargs)\
            .order_by("date desc", "line", "dir")\
            .all()
        
        for r in records:
            line = r.line
            dir = r.dir
            on_stop = r.on.stop_name
            off_stop = r.off.stop_name
            date = r.date.strftime(DATE)
            time = r.date.strftime(TIME)
            user = r.user_id
            rows.append(
                {'date':date,
                 'time':time,
                 'user':user,
                 'line': line,
                 'dir': DIRECTION[str(dir)],
                 'on': on_stop,
                 'off': off_stop})

        return rows

    @staticmethod
    def routes():
        """returns sorted list of route numbers in database"""
        routes = []
        scans = db.session.query(Scans.line)\
            .group_by(Scans.line)\
            .order_by(Scans.line)\
            .all()
        stops = db.session.query(OnOffPairs_Stops.line)\
            .group_by(OnOffPairs_Stops.line)\
            .order_by(OnOffPairs_Stops.line)\
            .all()

        for s in scans:
            routes.append(s.line)
        for s in stops:
            routes.append(s.line)
        return routes

