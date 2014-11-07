import csv, os

from sqlalchemy import func, desc, distinct, cast, Integer

from flask import current_app
#from api.shared.models import Scans, OnOffPairs_Scans, OnOffPairs_Stops
from api import db, web_session
from api import debug

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
                    app.logger.debug(time)
                    app.logger.debug(stats)
                    if not (stats['count'] == 0 or stats['target'] == 0):
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

        RTE = 0
        RTE_DESC = 1
        ret_val = [ {'rte':str(route[RTE]), 'rte_desc':route[RTE_DESC]}
            for route in routes ]
        
        return ret_val

    @staticmethod
    def get_directions():
        ret_val = []
        directions = web_session.execute("""
            SELECT rte, rte_desc, dir, dir_desc
            FROM v.lookup_dir
            ORDER BY rte, dir;""")

        RTE = 0
        RTE_DESC = 1
        DIR = 2
        DIR_DESC = 3

        ret_val = [ {'rte':str(direction[RTE]), 'rte_desc':direction[RTE_DESC],
            'dir':int(direction[DIR]), 'dir_desc':direction[DIR_DESC]}
            for direction in directions ]
        app.logger.debug(ret_val)

        return ret_val




    @staticmethod
    def query_route_data(rte_desc='', dir_desc=''):
        ret_val = []
        debug("query: " + rte_desc + ' ' + dir_desc)

        # query last 100 most recent
        # records for route and direction passed in
        # TODO method to build query instead of having three..
        if rte_desc and dir_desc:
            debug('rte and dir')
            query = web_session.execute("""
                SELECT rte_desc, dir_desc, date, time, user_id,
                    on_stop_name, off_stop_name
                FROM v.display_data
                WHERE rte_desc = :rte_desc
                AND dir_desc = :dir_desc
                ORDER BY date DESC, time DESC
                LIMIT 100;""", {'rte_desc':rte_desc, 'dir_desc':dir_desc})
        elif rte_desc:
            debug('just_dir')
            query = web_session.execute("""
                SELECT rte_desc, dir_desc, date, time, user_id,
                    on_stop_name, off_stop_name
                FROM v.display_data
                WHERE rte_desc = :rte_desc
                ORDER BY date DESC, time DESC
                LIMIT 100;""", {'rte_desc':rte_desc})
        else:
            debug('other')
            query = web_session.execute("""
                SELECT rte_desc, dir_desc, date, time, user_id,
                    on_stop_name, off_stop_name
                FROM v.display_data
                ORDER BY date DESC, time DESC
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
      
        debug(ret_val)
        return ret_val


    @staticmethod
    def query_route_status(rte_desc=''):
        # set rte_desc to wildcard to query
        # if no route was specified
        ret_val = {}
      
        # query web database
        # using helper views
        
        if rte_desc:
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
            ret_val = Helper.build_response_route_status(query)

        else:
            # query web database
            # using helper views
            query = web_session.execute("""
                SELECT rte, rte_desc, dir, dir_desc,
                    time_period, count, target
                FROM v.summary
                ORDER BY rte, dir,
                    CASE time_period
                        WHEN 'AM Peak' THEN 1
                        WHEN 'Midday' THEN 2
                        WHEN 'PM Peak' THEN 3
                        WHEN 'Evening' THEN 4
                        WHEN 'Total' THEN 5
                    ELSE 6
                    END;""")
            ret_val = Helper.build_response_summary_status(query)
          
       
       
        return ret_val

    @staticmethod
    def build_shell(dir_desc):
        ret_val = {}
        ret_val['dir_desc'] = dir_desc
        ret_val['AM Peak'] = {}
        ret_val['Midday'] = {}
        ret_val['PM Peak'] = {}
        ret_val['Evening'] = {}
        return ret_val


    @staticmethod
    def build_response_summary_status(query):
        ret_val = {}
        
        for record in query:
            rte = int(record[0])
            rte_desc = record[1]
            dir = int(record[2])
            dir_desc = record[3]
            time = record[4]
            count = int(record[5])
            target = int(record[6])

            data = {}
            data['target'] = target
            data['count'] = count

            if rte_desc not in ret_val:
                ret_val[rte_desc] = {}

            # set up each time period of this direction
            # populate later when that record is fetched
            if str(dir) not in ret_val[rte_desc]:
                ret_val[rte_desc][str(dir)] = Helper.build_shell(dir_desc)
   
            if target == 0:
                data = {}

            ret_val[rte_desc][str(dir)][time] = data
        
        return ret_val
    
    @staticmethod
    def build_response_route_status(query):
        ret_val = {}

        # look through query results
        # and build response
        for record in query:
            rte = int(record[0])
            rte_desc = record[1]
            dir = int(record[2])
            dir_desc = record[3]
            time = record[4]
            count = int(record[5])
            target = int(record[6])
            
            data = {}
            data['target'] = target
            data['count'] = count

            # add route description
            # only executes in first loop
            if 'rte_desc' not in ret_val:
                ret_val['rte_desc'] = rte_desc
            
            # build dictionary for each time period
            if str(dir) not in ret_val:
                ret_val[str(dir)] = Helper.build_shell(dir_desc)
            
            # set target and count data into correct
            # direction and time period
            if target == 0:
                data = {}
            
            ret_val[str(dir)][time] = data
        
        return ret_val

