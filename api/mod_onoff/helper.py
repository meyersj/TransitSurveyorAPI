import csv, os

from sqlalchemy import func, desc, distinct, cast, Integer

from flask import current_app
#from api.shared.models import Scans, OnOffPairs_Scans, OnOffPairs_Stops
from api import db, web_session

app = current_app

GREEN_STATUS = '#76DB55'
RED_STATUS = '#DB5555'
INBOUND = '1'
OUTBOUND = '0'
DIRECTION = {'1':'Inbound', '0':'Outbound'}
TRAINS = ['190','193','194','200']

class Helper(object):

    # return total number of records for each route being surveyed
    @staticmethod
    def summary_status_query():
        # TODO add union for streetcar data
        ret_val = []
      
        # get count and target for each route
        query = web_session.execute("""
            SELECT 
                rte,
                rte_desc,
                sum(count) AS count,
                sum(target) AS target
            FROM v.summary
            GROUP BY rte, rte_desc
            ORDER BY rte;""")
        
        # indexes for tuples returned by query
        RTE = 0
        RTE_DESC = 1
        COUNT = 2
        TARGET = 3

        # build data for each route
        # and add to ret_val list
        # sorted by route number
        for record in query:
            data = {}
            data['rte'] = str(record[RTE])
            data['rte_desc'] = record[RTE_DESC]
            data['count'] = float(record[COUNT])
            data['target'] = float(record[TARGET])
            ret_val.append(data)

        return ret_val

    @staticmethod
    def summary_chart():
        status = Helper.summary_status_query() 
        categories = []
        remaining = []
        complete = []
        
        for record in status:
            pct = round((record['count'] / record['target']) * 100)
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

        # TODO handle case for streetcar routes 
        # seperate categories - no time of day?
        
        categories = []
        remaining = []
        complete = []

        times = ("AM Peak", "Midday", "PM Peak", "Evening")
       
        # build categories "<Direction> <Time Period>" label
        for direction in ['0', '1']:
            for time in times:
                stats = data[direction][time]
                # if we have data for that time period
                # add a record to 
                if stats:
                    categories.append(time + ": " + data[direction]['dir_desc'])
                    pct = 0
                    if stats['count'] != 0:
                        count = float(stats['count'])
                        target = float(stats['target'])
                        pct = round((count / target) * 100, 2)
                    
                    remaining.append(100 - pct)
                    complete.append(pct)
        
        series = [
            {'data':remaining, 'name':'remaining', 'color':RED_STATUS},
            {'data':complete, 'name':'complete', 'color':GREEN_STATUS}
        ]
        
        return {'series':series, 'categories':categories}

    @staticmethod
    def get_routes():
        ret_val = []

        routes = web_session.execute("""
            SELECT rte, rte_desc
            FROM v.lookup_rte
            ORDER BY rte;""")

        ret_val = [ {'rte':str(route[0]), 'rte_desc':route[1]}
            for route in routes ]
        
        return ret_val

    @staticmethod
    def query_route_data(rte_desc):
        ret_val = []
      
        # query last 100 most recent
        # records for route passed in
        
        app.logger.debug(rte_desc)        
        if rte_desc and rte_desc != 'All': 
            query = web_session.execute("""
                SELECT rte_desc, dir_desc, date, time, user_id,
                    on_stop_name, off_stop_name
                FROM v.display_data
                WHERE rte_desc = :rte_desc
                ORDER BY date, time DESC
                LIMIT 100;""", {'rte_desc':rte_desc})
        else:
            query = web_session.execute("""
                SELECT rte_desc, dir_desc, date, time, user_id,
                    on_stop_name, off_stop_name
                FROM v.display_data
                ORDER BY date, time DESC
                LIMIT 100;""")

        RTE_DESC = 0
        DIR_DESC = 1
        DATE = 2
        TIME = 3
        USER = 4
        ON_STOP = 5
        OFF_STOP = 6

        # each record will be converted as json
        # and sent back to page
        for record in query:
            data = {}
            data['date'] = str(record[DATE])
            data['time'] = str(record[TIME])
            data['user'] = record[USER]
            data['rte_desc'] = record[RTE_DESC]
            data['dir_desc'] = record[DIR_DESC]
            data['on_stop'] = record[ON_STOP]
            data['off_stop'] = record[OFF_STOP]
            ret_val.append(data)
       
        return ret_val

    @staticmethod
    def query_route_status(rte_desc):
        ret_val = {}
       
        # query web database
        # using helper views
        query = web_session.execute("""
            SELECT rte, rte_desc, dir, dir_desc,
                time_period, count, target
            FROM v.summary
            WHERE rte_desc = :rte_desc
            ORDER BY rte, dir,
                CASE time_period
                    WHEN 'AM Peak' THEN 1
                    WHEN 'Midday' THEN 2
                    WHEN 'PM Peak' THEN 3
                    WHEN 'Evening' THEN 4
                    WHEN 'Total' THEN 5
                ELSE 6
                END;""", {'rte_desc':rte_desc})
        
        # index for each tuple in query results
        RTE = 0
        RTE_DESC = 1
        DIR = 2
        DIR_DESC = 3
        TIME = 4
        COUNT = 5
        TARGET = 6

        def build_shell(dir_desc):
            ret_val = {}
            ret_val['dir_desc'] = dir_desc
            ret_val['AM Peak'] = {}
            ret_val['Midday'] = {}
            ret_val['PM Peak'] = {}
            ret_val['Evening'] = {}
            return ret_val

        # look through query results
        # and build response
        for record in query:
            str_dir = str(record[DIR])
            data = {}
            data['target'] = int(record[TARGET])
            data['count'] = int(record[COUNT])

            # add route description
            # only executes in first loop
            if record[RTE_DESC] not in ret_val:
                ret_val['rte_desc'] = record[RTE_DESC]
            
            # build dictionary for each time period
            if str_dir not in ret_val:
                ret_val[str_dir] = build_shell(record[DIR_DESC])
            
            # set target and count data into correct
            # direction and time period
            ret_val[str_dir][record[TIME]] = data
       
        return ret_val

