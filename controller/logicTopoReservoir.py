from sqlalchemy.sql.functions import func
from model.db import db
import json
from controller.util import DictToGeoJsonProp,MergeRowsToGeoJson
from controller.style import *
from colour import Color

class LogicTopoReservoir():
    def FindStorageArea(self,param):
        if not "nodeID" in param:
            return {"error":"no id parameter"}
        nodeID = param["nodeID"]
        sql = "select name as id,name,ST_AsGeoJson(ST_Transform(ST_SetSRID(geom,3826),4326))::json as geom from ressub where name='%s';" % nodeID
        row = db.engine.execute(sql).first()
        if row is None:
            return {"error": "查無蓄水範圍資料"}
        row = dict(row)

        row["geom"] = DictToGeoJsonProp(row)
        row["geom"]["properties"]["color"] = "#fff"
        row["layer"] = SubbasinStyle(fillKey="color")
        if "format" in param and param["format"] == "geojson":
            return row["geom"]
        return {
            "nodeID":row["id"],
            "nodeName":row["name"],
            "data":[row]
        }

    def FindCatchment(self,param):
        if not "nodeID" in param:
            return {"error":"no id parameter"}
        nodeID = param["nodeID"]
        sql = "select name as id,name,ST_AsGeoJson(ST_Transform(ST_SetSRID(geom,3826),4326))::json as geom from reservoir where name='%s';" % nodeID
        row = db.engine.execute(sql).first()
        if row is None:
            return {"error": "查無集水區資料"}
        row = dict(row)

        row["geom"] = DictToGeoJsonProp(row)
        row["layer"] = SubbasinStyle()
        if "format" in param and param["format"] == "geojson":
            return row["geom"]
        return {
            "nodeID":row["id"],
            "nodeName":row["name"],
            "data":[row]
        }