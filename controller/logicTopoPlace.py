from sqlalchemy.sql.functions import func
from model.db import db
import json
from controller.util import DictToGeoJsonProp

class LogicTopoPlace():
    def FindVillageByLatLng(self,param):
        if not "lat" in param or not "lng" in param:
            return {"error":"no location parameter"}
        lat = param["lat"]
        lng = param["lng"]
        sql = "select countyname,townname,villname as title,ST_AsGeoJson(ST_Transform(ST_SetSRID(sim_geom,3826),4326))::json as geom from village_moi_121 where ST_Contains(ST_Transform(ST_SetSRID(sim_geom,3826),4326),ST_SetSRID(ST_POINT(%s,%s),4326));" % (lng,lat)
        #sql = "select countyname,townname as title, ST_AsGeoJson(ST_Transform(ST_SetSRID(sim_geom,3824),4326))::json as geom from town_moi where ST_Contains(ST_Transform(ST_SetSRID(sim_geom,3824),4326),ST_SetSRID(ST_POINT(%s,%s),4326));" % (lng,lat)
        #sql = "select countyname as title, ST_AsGeoJson(ST_Transform(ST_SetSRID(sim_geom,3824),4326))::json as geom from county_moi where ST_Contains(ST_Transform(ST_SetSRID(sim_geom,3824),4326),ST_SetSRID(ST_POINT(%s,%s),4326));" % (lng,lat)
        row = db.engine.execute(sql).first()
        if row is None:
            return {"error": "無村里資料"}
        row = dict(row)

        row["geom"] = DictToGeoJsonProp(row)
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
        v = db.engine.execute(sql).first()
        if v is None:
            return {"error": "無淨水廠資料"}
        v = dict(v)
        
        #get water work info
        sql = "select 淨水場名稱 as title,主要供水轄區,原水來源,ST_AsGeoJson(ST_Transform(ST_SetSRID(geom,3826),4326))::json as geom from m_waterwork_area where \"淨水場名稱\"='%s';" % v["WATERWORK"]
        row = db.engine.execute(sql).first()
        if row is None:
            return {"error": "無淨水廠資料"}
        row = dict(row)
        
        row["geom"] = DictToGeoJsonProp(row)
        row["layer"] = [{
                "type": "symbol",
                "layout":{
                    "icon-image": "waterwork",
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
        if not "nodeID" in param:
            return {"error":"no nodeID parameter"}
        #get waterwork name from village
        nodeID = param["nodeID"]
        sql = "select * from s_village_waterin where \"VILLNAME\" = '%s';" % nodeID
        v = db.engine.execute(sql).first()
        if v is None:
            return {"error": "無取水口資料"}
        v = dict(v)
        
        #get water work info
        sql = "select name as title,ST_AsGeoJson(ST_Transform(ST_SetSRID(geom,3826),4326))::json as geom from s_waterin_b where name='%s';" % v["WATERIN"]
        row = db.engine.execute(sql).first()
        if row is None:
            return {"error": "無取水口資料"}
        row = dict(row)
        
        row["geom"] = DictToGeoJsonProp(row)
        row["layer"] = [{
                "type": "symbol",
                "layout":{
                    "icon-image": "waterin",
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