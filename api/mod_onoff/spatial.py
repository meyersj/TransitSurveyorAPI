import os
import json

from flask import current_app
from api import db
from api import Session
from api import debug

app = current_app



class Spatial(object):

    @staticmethod
    def get_tad_centroid(rte_desc, dir_desc):
        
        if not rte_desc:
            rte_desc = "%"
        if not dir_desc:
            dir_desc = "%"
        ret_val = []
        web_session = Session()
        query = web_session.execute("""
            SELECT rte_desc, tad_gid, sum(ons),
                ST_AsGeoJSON(ST_Transform(ST_Centroid(ST_Union(geom)), 4326))
            FROM stop_tad
            WHERE rte_desc = :rte_desc
            GROUP BY rte_desc, tad_gid
            ORDER BY rte_desc, tad_gid;""",
            {"rte_desc":rte_desc}
        )
        for r in query:
            geojson = {}
            properties = {}
            properties["rte_desc"] = str(r[0])
            #properties["dir_desc"] = str(r[1])
            properties["tad"] = str(r[1])
            properties["sum"] = str(r[2])
            geojson["type"] = "Feature"
            geojson["geometry"] = json.loads(str(r[3]))
            geojson["properties"] = properties
            ret_val.append(geojson) 
        web_session.close()
        return ret_val
    
    @staticmethod
    def get_tad_stops(rte):
        web_session = Session()
        query = web_session.execute("""
            SELECT
                rte,
                dir,
                stop_id,
                sum(ons),
                ST_AsGeoJSON(min(ST_Transform(geom, 4326))),
                tad_gid
            FROM apc_time_stops
            WHERE rte_desc = 4 AND dir = 0
            GROUP BY tad_gid, stop_id, rte, dir;""") 
        ret_val = []
        for r in query:
            geojson = {}
            properties = {}
            properties["rte"] = str(r[0])
            properties["dir"] = str(r[1])
            properties["stop_id"] = str(r[2])
            geojson["type"] = "Feature"
            geojson["geometry"] = json.loads(str(r[4]))
            geojson["properties"] = properties
            ret_val.append(geojson) 
        web_session.close()
        return ret_val   
                
        

