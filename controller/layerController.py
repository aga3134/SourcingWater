from sqlalchemy.sql.functions import func
from model.db import db
import json
from controller.util import MergeRowsToGeoJson

class LayerController():
    def GetBasin(self):
        sql = "select basin_no,basin_name,area,ST_AsGeoJson(ST_Transform(ST_SetSRID(geom,3826),4326))::json as geom from basin;"
        rows = db.engine.execute(sql)
        geom = MergeRowsToGeoJson(rows,idKey="basin_no",skipArr=["geom"])

        #generate json_def
        data = {
            "geom": geom,
            "layer": [
                {
                    "type":"line",
                    "paint": {
                        "line-color":"#fff",
                        "line-width":1
                    },
                },
                {
                    "type":"fill",
                    "paint":{
                        "fill-color":"#f33",
                        "fill-opacity":[
                            "case",
                            ["boolean", ["feature-state", "hover"], False],
                            0.5, 0
                        ]
                    }
                }
            ]
        }
        return {
            "layerName": "流域",
            "data": [data]
        }

    def GetRainStation(self):
        sql = "select * from r_rain_station;"
        rows = db.engine.execute(sql)
        arr = []
        for row in rows:
            d = dict(row)
            d["geom"] = {
                "type": "Point",
                "coordinates": [float(d["lon"]),float(d["lat"])]
            }
            arr.append(d)
        geom = MergeRowsToGeoJson(arr,idKey="stationID",skipArr=["geom","lat","lon"])
        
        #generate json_def
        data = {
            "geom": geom,
            "layer": [
                {
                    "type": "symbol",
                    "layout":{
                        "icon-image": "rain-station",
                        "text-field": ["get", "name"],
                        "text-size": 12,
                        "text-offset": [0, 1.25],
                        "text-anchor": "top"
                    },
                    "paint":{
                        "text-color": "#ff3"
                    }
                }
            ],
        }
        #print(data)
        return {
            "layerName": "雨量站",
            "data": [data]
        }

    def GetFloodStation(self):
        sql = "select * from r_flood_station;"
        rows = db.engine.execute(sql)
        arr = []
        for row in rows:
            d = dict(row)
            d["geom"] = {
                "type": "Point",
                "coordinates": [float(d["lng"]),float(d["lat"])]
            }
            arr.append(d)
        geom = MergeRowsToGeoJson(arr,idKey="_id",skipArr=["geom","lat","lng"])

        #generate json_def
        data = {
            "geom": geom,
            "layer": [
                {
                    "type": "symbol",
                    "layout":{
                        "icon-image": "flood-station",
                        "text-field": ["get", "stationName"],
                        "text-size": 12,
                        "text-offset": [0, 1.25],
                        "text-anchor": "top"
                    },
                    "paint":{
                        "text-color": "#ff3"
                    }
                }
            ],
        }
        #print(data)
        return {
            "layerName": "淹水測站",
            "data": [data]
        }