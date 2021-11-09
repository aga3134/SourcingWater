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

    def FindProtectArea(self,param):
        if not "nodeID" in param:
            return {"error":"no id parameter"}
        nodeID = param["nodeID"]
        
        #找蓄水範圍外1公里範圍
        sql = "select name as id,name,ST_AsEWKT(ST_Buffer(geom,1000)) as geom from ressub where name='%s';" % (nodeID)
        row = db.engine.execute(sql).first()
        if row == None:
            return {"error": "查無水庫資料"}

        reservoirGeom = "ST_SetSRID(ST_GeomFromEWKT('%s'),3826)" % row["geom"]
        sql = "select gid as id,polyname as name,ST_AsGeoJson(ST_Transform(ST_SetSRID(geom,3826),4326))::json as geom from twqprot where ST_Intersects(ST_SetSRID(geom,3826),%s);" % (reservoirGeom)
        #print(sql)
        rows = db.engine.execute(sql).fetchall()
        if len(rows) == 0:
            return {"error": "此水庫附近無水質水量保護區"}
        arr = []
        for row in rows:
            d = dict(row)
            d["geom"] = d["geom"]
            arr.append(d)

        geom = MergeRowsToGeoJson(arr,idKey="id",skipArr=["geom"])

        data = {}
        data["geom"] = geom
        data["layer"] = SubbasinStyle()
        if "format" in param and param["format"] == "geojson":
            return geom
        return {
            "nodeID":rows[0]["id"],
            "nodeName":rows[0]["name"],
            "data":[data]
        }