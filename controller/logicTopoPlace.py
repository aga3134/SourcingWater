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

    def FindVillageWaterwork(self,param):
        if not "nodeID" in param:
            return {"error":"no nodeID parameter"}
        #get waterwork name from village
        nodeID = param["nodeID"]
        sql = "select * from s_village_waterin where \"VILLNAME\" = '%s';" % nodeID
        v = dict(db.engine.execute(sql).first())
        print(sql)
        
        #get water work info
        sql = "select 淨水場名稱 as title,主要供水轄區,原水來源,ST_AsGeoJson(ST_Transform(ST_SetSRID(geom,3826),4326))::json as geom from m_waterwork_area where \"淨水場名稱\"='%s';" % v["WATERWORK"]
        row = dict(db.engine.execute(sql).first())
        
        row["layer"] = [{
                "type": "symbol",
                "layout":{
                    "icon-image": "red-marker",
                    "text-field": ["get", "title"],
                    "text-size": 12,
                    "text-offset": [0, 1.25],
                    "text-anchor": "top"
                },
                "paint":{
                    "text-color": "#ff3"
                }
            }]
        return {
            "nodeID":row["title"],
            "nodeName":row["title"],
            "data":[row]
        }

    def FindVillageWaterin(self,param):
        pass