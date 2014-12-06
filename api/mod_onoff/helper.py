import csv, os

from sqlalchemy import func, desc, distinct, cast, Integer

from flask import current_app
#from api.shared.models import Scans, OnOffPairs_Scans, OnOffPairs_Stops
from api import db
from api import Session
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
        web_session = Session()
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
        web_session.close()

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
        
        web_session = Session()
        routes = web_session.execute("""
            SELECT rte, rte_desc
            FROM v.lookup_rte
            ORDER BY rte;""")

        RTE = 0
        RTE_DESC = 1
        ret_val = [ {'rte':str(route[RTE]), 'rte_desc':route[RTE_DESC]}
            for route in routes ]
        web_session.close()
        
        return ret_val

    @staticmethod
    def get_directions():
        ret_val = []
        web_session = Session()
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
        web_session.close()
        return ret_val




    @staticmethod
    def query_route_data(user='', rte_desc='', dir_desc='', csv=False):
        ret_val = []
        query_args = {}       
        where = ""

        if user: user = "%" + user + "%"
        user_filter = " user_id LIKE :user "
        rte_desc_filter = " rte_desc = :rte_desc "
        dir_desc_filter = " dir_desc = :dir_desc "
        
        def construct_where(string, param, filt_name):
            if not param:
                return string

            if filt_name == "user": filt = user_filter
            elif filt_name == "rte_desc": filt = rte_desc_filter
            else: filt = dir_desc_filter

            if string:
                return string + " AND " + filt
            else:
                return string + filt
      
        # build where clause
        debug(where)
        for param in [(user, 'user'),(rte_desc, 'rte_desc'),(dir_desc, 'dir_desc')]:
            where = construct_where(where, param[0], param[1])
            debug(where)
            
            query_args[param[1]] = param[0]
        if where:
            where = " WHERE " + where
        
        limit = "LIMIT 300;"
        if csv:
            # add headers to csv data
            ret_val.append(
                ['date','time','user','rte_desc','dir_desc','on_stop', 'off_stop'])
            
            limit = ";"
 
        query_string = """
            SELECT rte_desc, dir_desc, date, time, user_id,
                on_stop_name, off_stop_name
            FROM v.display_data """
        query_string += where 
        query_string += " ORDER BY date DESC, time DESC "
        query_string += limit

        debug(query_string)

        web_session = Session()
        query = web_session.execute(query_string, query_args)

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
            if csv:
                data = []
                data.append(str(record[DATE]))
                data.append(str(record[TIME]))
                data.append(record[USER])
                data.append(record[RTE_DESC])
                data.append(record[DIR_DESC])
                data.append(record[ON_STOP])
                data.append(record[OFF_STOP])
            else:
                data = {}
                data['date'] = str(record[DATE])
                data['time'] = str(record[TIME])
                data['user'] = record[USER]
                data['rte_desc'] = record[RTE_DESC]
                data['dir_desc'] = record[DIR_DESC]
                data['on_stop'] = record[ON_STOP]
                data['off_stop'] = record[OFF_STOP]
            ret_val.append(data)
        web_session.close()
        return ret_val


    @staticmethod
    def query_route_status(rte_desc=''):
        # set rte_desc to wildcard to query
        # if no route was specified
        ret_val = {}
      
        # query web database
        # using helper views
       
        web_session = Session()
        if rte_desc:
            query = web_session.execute("""
                SELECT rte, rte_desc, dir, dir_desc,
                    time_period, count, target * .2
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
                    time_period, count, target * .2
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
        web_session.close()
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

     
    @staticmethod
    def current_users(date):
        ret_val = {}
        
        web_session = Session()
        results = web_session.execute("""
            SELECT rte_desc, time_period, user_id, rte
            FROM v.users_tod
            WHERE date = :date
            ORDER BY
            CASE time_period
                WHEN 'AM Peak' THEN 1
                    WHEN 'Midday' THEN 2
                    WHEN 'PM Peak' THEN 3
                    WHEN 'Evening' THEN 4
                    WHEN 'Total' THEN 5
                ELSE 6
            END, rte;""",{'date':date})

            
        for result in results:
            
            rte_desc = result[0]
            time_period = result[1]
            
            user = ", ".join(
                sorted(list(set([user.strip() for user in result[2].split(",")]))))
            
            #list1 = result[2].split(",")
            #list2 = set(list1)
            #list3 = ", ".join(list2)
            #debug(list1)
            #debug(list2)
            #debug(list3)
            #user = ", ".join(list(set(result[2].split(","))))
            #debug(user)
            if time_period not in ret_val:
                ret_val[time_period] = []
            
            data = {'rte_desc':rte_desc, 'user':user}
            ret_val[time_period].append(data)
        web_session.close() 
        debug(ret_val)
        return ret_val

    @staticmethod
    def get_users():
        #users = ["Twaller", "Rpeabody", "kweaver", "dloftus"]
        users = [
            "aggreye", "aronsonr",
            "bishopk", "brockq", "cumminga", "dbower",
            "dloftus", "elkingtj", "hamiltob", "herzogn",
            "hickeyj", "kweaver", "langstoe", "longj",
            "meyersj", "pala", "petersry", "rogerss",
            "Rpeabody", "schoenbi", "sheehana", "testuser",
            "turnera", "Twaller", "wagnerz", "willeyc"
        ] 
        return sorted(users)






