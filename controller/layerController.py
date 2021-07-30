from sqlalchemy.sql.functions import func
from model.db import db
import json

class LayerController():
    def GetBasin(self):
        sql = "select basin_no,basin_name,area,ST_AsGeoJson(ST_Transform(ST_SetSRID(geom,3826),4326))::json as geom from basin;"
        rows = db.engine.execute(sql)
        #merge all rows to one geojson feature collection
        geom = {}
        geom["type"] = "FeatureCollection"
        geom["features"] = []
        for row in rows:
            d = dict(row)
            f = {}
            f["type"] = "Feature"
            f["geometry"] = d["geom"]
            p = {}
            for key in d:
                if key == "geom":
                    continue
                p[key] = d[key]
            p["opacity"] = 0
            f["id"] = p["basin_no"]
            f["properties"] = p
            geom["features"].append(f)
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
        #merge all rows to one geojson feature collection
        geom = {}
        geom["type"] = "FeatureCollection"
        geom["features"] = []
        for row in rows:
            d = dict(row)
            f = {}
            f["type"] = "Feature"
            f["geometry"] = {
                "type": "Point",
                "coordinates": [float(d["lon"]),float(d["lat"])]
            }
            p = {}
            for key in d:
                if key in ["lat","lon"]:
                    continue
                p[key] = d[key]
            f["id"] = p["stationID"]
            f["properties"] = p
            geom["features"].append(f)
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
        #merge all rows to one geojson feature collection
        geom = {}
        geom["type"] = "FeatureCollection"
        geom["features"] = []
        for row in rows:
            d = dict(row)
            f = {}
            f["type"] = "Feature"
            f["geometry"] = {
                "type": "Point",
                "coordinates": [float(d["lng"]),float(d["lat"])]
            }
            p = {}
            for key in d:
                if key in ["lat","lng"]:
                    continue
                p[key] = d[key]
            f["id"] = p["_id"]
            f["properties"] = p
            geom["features"].append(f)
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