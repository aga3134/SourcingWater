from sqlalchemy.sql.functions import func
from model.db import db
import json
from controller.util import DictToGeoJsonProp,MergeRowsToGeoJson
from controller.style import *
from colour import Color

class LogicTopoDebris():
    def FindCatchment(self,param):
        if not "nodeID" in param:
            return {"error":"no id parameter"}
        nodeID = param["nodeID"]
        sql = "select debrisno as id,debrisno as name,ST_AsGeoJson(ST_Transform(ST_SetSRID(wkb_geometry,3826),4326))::json as geom from watershed1726 where debrisno='%s';" % nodeID
        row = db.engine.execute(sql).first()
        if row is None:
            return {"error": "無集水區資料"}
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

    def FindInfluence(self,param):
        if not "nodeID" in param:
            return {"error":"no id parameter"}
        nodeID = param["nodeID"]
        sql = "select debrisno as id,debrisno as name,risk,ST_AsGeoJson(ST_Transform(ST_SetSRID(wkb_geometry,3826),4326))::json as geom from debris1726 where debrisno='%s';" % nodeID
        row = db.engine.execute(sql).first()
        if row is None:
            return {"error": "無影響範圍資料"}
        row = dict(row)

        row["geom"] = DictToGeoJsonProp(row)
        #setup color
        feat = row["geom"]
        risk = feat["properties"]["risk"]
        if risk == "低":
            feat["properties"]["color"] = "#33f"
        elif risk == "中":
            feat["properties"]["color"] = "#ff3"
        elif risk == "高":
            feat["properties"]["color"] = "#f33"
        elif risk == "持續觀察":
            feat["properties"]["color"] = "#fff"

        row["layer"] = SubbasinStyle(fillKey="color")
        if "format" in param and param["format"] == "geojson":
            return row["geom"]
        return {
            "nodeID":row["id"],
            "nodeName":row["name"],
            "data":[row]
        }

    def FindHistoryPhoto(self,param):
        pass

    def FindFlowPath(self,param):
        if not "nodeID" in param:
            return {"error":"no id parameter"}
        nodeID = param["nodeID"]
        sql = "select debrisno as id,debrisno as name,ST_AsGeoJson(ST_Transform(ST_SetSRID(wkb_geometry,3826),4326))::json as geom from debrisstream1726 where debrisno='%s';" % nodeID
        row = db.engine.execute(sql).first()
        if row is None:
            return {"error": "無流路資料"}
        row = dict(row)

        row["geom"] = DictToGeoJsonProp(row)
        row["layer"] = FlowPathStyle(lineWidth=1)
        if "format" in param and param["format"] == "geojson":
            return row["geom"]
        return {
            "nodeID":row["id"],
            "nodeName":row["name"],
            "data":[row]
        }