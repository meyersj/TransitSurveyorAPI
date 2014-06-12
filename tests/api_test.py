import requests
import random
import urlparse
import datetime
import csv

UUID = 'uuid'
DATE = 'date'
LINE = 'rte'
DIR = 'dir'
MODE = 'mode'
LAT = 'lat'
LON = 'lon'
ON_STOP = 'on_stop'
OFF_STOP = 'off_stop'
URL = 'url'
TYPE = 'type'
INSERT_SCAN = 'insertScan'
INSERT_PAIR = 'insertPair'

LAT_LOW = 44.5
LAT_HIGH = 45.5
LON_LOW = -122.5
LON_HIGH = -121.5

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
TEST_MAX = 5

"""
Takes dictionary of parameters, builds up the HTTP POST request.
When run() method is called the request is sent to server and response is returned
"""

class Test(object):
    test_type = None
    url = None
    params = {}
   
    def __init__(self, data):
        self.test_type = data[TYPE]
        self.params = self.build_params(data) 
        self.url = self.build_url(data[URL])
    
    def build_params(self, data):
        params = {}
        params[DATE] = data[DATE]
        params[LINE] = data[LINE]
        params[DIR] = data[DIR]

        if self.test_type == "scan":
            params[UUID] = data[UUID]
            params[MODE] = data[MODE]
            params[LAT] = data[LAT]
            params[LON] = data[LON]
        #self.test_type == "pair"
        else:
            params[ON_STOP] = data[ON_STOP]
            params[OFF_STOP] = data[OFF_STOP]
  
        return params
 
    def build_url(self, url):
        if self.test_type == "scan":
            path = INSERT_SCAN
        #self.test_type == "pair"
        else:
            path = INSERT_PAIR
        
        url = urlparse.urljoin(url, path)
        return url
         

    def run(self):
        response = requests.post(self.url, data=self.params)
        return response

class TestRunner(object):
    success = 0
    fail = 0
    url = None
    #scan_routes = [route1, route2, ... ]
    scan_routes = None
    #pair_routes = {rte:{inbound:[stop1, stop2, ... ], outbound:[stop1, stop2, ... ]}}
    pair_routes = None
    tests = []

    def __init__(self, url, scan_routes, pair_routes):
        self.url = url
        self.scan_routes, self.pair_routes = self.open_routes(scan_routes, pair_routes)

        self.build_pair_tests()
        self.build_scan_tests()
        self.run_tests()
       
    #TODO build data structure with scanning routes, and pair routes
    #for pair routes include all inbound and outbound stops
    #to be randomly selected

    def open_routes(self, scan_routes, pair_routes):
        scan_routes_list = []
        pair_routes_dict = {}
        try:
            with open(scan_routes, 'r') as csvfile:
                reader = csv.reader(csvfile)
                
                for row in reader:
                    scan_routes_list.append(row[0])
        except IOError:
            pass
            #log cannot open routes file

        try:
            with open(pair_routes, 'r') as csvfile:
                reader = csv.reader(csvfile)
                
                for row in reader:
                    if row[0] not in pair_routes_dict:
                        pair_routes_dict[row[0]] = {}
                        #in bound stops list
                        pair_routes_dict[row[0]]['0'] = []
                        #out bound stops list
                        pair_routes_dict[row[0]]['1'] = []

                    pair_routes_dict[row[0]][row[1]].append(row[2])
                    
        except IOError:
            pass
            #log error opening file
        
        return scan_routes_list, pair_routes_dict

    
    def scan_params(self, line, dir, uuid, mode):
        params = {}
        d = datetime.datetime.now()
        params[URL] = self.url
        params[LINE] = line
        params[DIR] = dir
        params[UUID] = uuid
        params[MODE] = mode
        params[DATE] = d.strftime(DATE_FORMAT)
        params[LAT] = random.uniform(LAT_LOW, LAT_HIGH)
        params[LON] = random.uniform(LON_LOW, LON_HIGH)
        params[TYPE] = "scan"
        return params


    def build_scan_tests(self):
        #loop through all routes
        for route in self.scan_routes:

            #loop for inbound tests
            dir = 0
            for x in range(0, TEST_MAX):
                uuid = random.randint(0, 1000)
                on_params = self.scan_params(route, dir, uuid, "on")
                off_params = self.scan_params(route, dir, uuid, "off")
                self.tests.append(on_params)
                self.tests.append(off_params)

            #loop for outboud tests       
            dir = 1
            for x in range(0, TEST_MAX):
                uuid = random.randint(0, 1000)
                on_params = self.scan_params(route, dir, uuid, "on")
                off_params = self.scan_params(route, dir, uuid, "off")
                self.tests.append(on_params)
                self.tests.append(off_params)


    def pair_params(self, line, dir, on_stop, off_stop):
        params = {}
        d = datetime.datetime.now()
        params[URL] = self.url
        params[LINE] = line
        params[DIR] = dir
        params[DATE] = d.strftime(DATE_FORMAT)
        params[ON_STOP] = on_stop
        params[OFF_STOP] = off_stop
        params[TYPE] = "pair"
        return params

    #TODO implement this
    def build_pair_tests(self):
        
        #loop through all pair routes
        for route, data in self.pair_routes.iteritems():
            
            routes = data['0']
            dir = 0
            for x in range(0, TEST_MAX):
                on_stop = random.choice(routes)  
                off_stop = random.choice(routes)
                
                params = self.pair_params(route, dir,  on_stop, off_stop)
                self.tests.append(params)

            routes = data['1']
            dir = 1
            for x in range(0, TEST_MAX):
                on_stop = random.choice(routes)  
                off_stop = random.choice(routes)
                
                params = self.pair_params(route, dir,  on_stop, off_stop)
                self.tests.append(params)




    def run_tests(self):
        
        for params in self.tests:
            test = Test(params)
            response = test.run()
            print response.status_code
            print response.text
            #TODO logging if tests fail
            if response.status_code == 200:
                self.success += 1
            else:
                self.fail += 1

    def get_results(self):
        return self.success, self.fail            

if __name__ == '__main__':
    
    scan_routes = "../data/scan_routes.csv"
    pair_routes = "../data/pair_routes.csv"

    url = "http://127.0.0.1:5000"

    test_runner = TestRunner(url, scan_routes, pair_routes)
    success, fail = test_runner.get_results()

    print "Passing tests: " + str(success)
    print "Failing tests: " + str(fail)
