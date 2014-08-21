from sqlalchemy import func, desc

from models import Scans, OnOffPairs_Scans, OnOffPairs_Stops
from api import db


GREEN_STATUS = '#76DB55'
RED_STATUS = '#DB5555'
INBOUND = '1'
OUTBOUND = '0'
DIRECTION = {'1':'Inbound', '0':'Outbound'}
TRAINS = ['190','193','194','200']
QUOTA = {
    '9':150,
    '17':150,
    '19':150,
    '28':150,
    '29':150,
    '30':150,
    '31':150,
    '32':150,
    '33':150,
    '34':150,
    '35':150,
    '70':150,
    '75':150,
    '99':150,
    '152':150,
    '190':150,
    '193':150,
    '194':150,
    '200':150}


def percent(amount, total):
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
        complete = 0
        rem_count = 0
        rem_total = 0
        results = {}

        for route in routes:
            data = {}
            count = Count.records(line=route)
            quota = QUOTA[str(route)]

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
        in_pct = percent(Count.records(line=line, dir=INBOUND), QUOTA[str(line)])
        out_pct = percent(Count.records(line=line, dir=OUTBOUND), QUOTA[str(line)])
        categories = ['Inbound', 'Outbound']
        series =  [
            {'data':[100 - in_pct, 100 - out_pct], 'name':'Remaining','color':RED_STATUS},
            {'data':[in_pct, out_pct], 'name':'Complete', 'color':GREEN_STATUS}]
        return {'series':series, 'categories':categories}

    @staticmethod
    def all_routes(routes):
        complete = []
    
        for route in routes:
            #TODO fetch total from table instead of hard coded
            pct = percent(Count.records(line=route), QUOTA[str(route)] * 2)
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

