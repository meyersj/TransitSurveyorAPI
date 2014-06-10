import requests
import random


UUID = 'uuid'
DATE = 'date'
LINE = 'rte'
DIR = 'dir'
MODE = 'mode'
LAT = 'lat'
LON = 'lon'



url_scan = "http://54.245.105.70:8493/insertScan"
url_pair = "http://54.245.105.70:8493/insertPair"






uuid = 15
date = "2014-12-14 12:13:14"
line = 9
dir = 0
mode = "off"
lat = 45
lon = -122
scan_data = { UUID:uuid, DATE:date, LINE:line, DIR:dir, MODE:mode, LAT:lat, LON:lon }


#r = requests.post(url, data=scan_data)
#print r.status_code
#print r.json
#print r.text


line = 9
dir = 1
lat_low = 44.5
lat_high = 45.5
lon_low = -122.5
lon_high = -121.5

for x in range(0,10):
    print "uuid: " + str(x)
    uuid = x
    date = "2014-12-14 12:00:00"
    mode = "on"
    lat = random.uniform(lat_low,lat_high)
    lon = random.uniform(lon_low,lon_high)

    on_data = { UUID:uuid, DATE:date, LINE:line, DIR:dir, MODE:mode, LAT:lat, LON:lon }
    r = requests.post(url_scan, data=on_data)
    print r.text  
    
    lat = random.uniform(lat_low,lat_high)
    lon = random.uniform(lon_low,lon_high)
    mode = "off"
    date = "2014-12-14 12:30:00"

    off_data = { UUID:uuid, DATE:date, LINE:line, DIR:dir, MODE:mode, LAT:lat, LON:lon }
    r = requests.post(url_scan, data=off_data)
    print r.text  




