from sqlalchemy.sql.functions import func
from model.db import db
import json

class LogicTopoPlace():
    def FindVillageByLatLng(self,param):
        if not "lat" in param or not "lng" in param:
            return {"error":"no location parameter"}
        lat = param["lat"]
        lng = param["lng"]
        sql = "select countyname,townname,villname as title,ST_AsGeoJson(ST_Transform(ST_SetSRID(geom,3826),4326))::json as geom from village_moi_121 where ST_Contains(ST_Transform(ST_SetSRID(geom,3826),4326),ST_SetSRID(ST_POINT(%s,%s),4326));" % (lng,lat)
        row = dict(db.engine.execute(sql).first())
        row["layer"] = [
            {
                "type": "line",
                "paint": {
                    "line-color": "#3f3",
                    "line-width": 4
                }
            }
        ]
        return {
            "nodeID":row["title"],
            "nodeName":row["title"],
            "data":[row]
        }
