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
            "title": "流域分佈",
            "geom": geom,
            "style": [
                {
                    "type":"line",
                    "paint":{
                        "line-color":"#fff",
                        "line-width":1
                    }
                },
                {
                    "type":"fill",
                    "paint":{
                        "fill-color":"#33f",
                        "fill-opacity":[
                            "case",
                            ["boolean", ["feature-state", "hover"], False],
                            0.5, 0
                        ]
                    }
                }
            ],
        }
        return {
            "data": [data]
        }