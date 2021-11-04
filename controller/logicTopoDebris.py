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
        if not "nodeID" in param:
            return {"error":"no nodeID parameter"}
        nodeID = param["nodeID"]
        nodeName = ""
        if "nodeName" in param:
            nodeName = param["nodeName"]

        #shape資訊不完整
        if not "shape" in param:
            return {
                "info":"請點選要查詢的位置",
                "nodeID":nodeID,
                "nodeName":nodeName,
                "setting":{
                    "shapeConfig":{
                        "type":"circle",
                        "variable": "shape",
                        "fixedRadius": 3000,
                        "layer": CircleStyle()
                    }
                }
            }
        shape = json.loads(param["shape"])

        lat = shape["center"][1]
        lng = shape["center"][0]
        radius = shape["radius"]
        pt = "ST_Transform(ST_SetSRID(ST_POINT(%s,%s),4326),3826)" % (lng,lat)
        geom = "ST_Transform(ST_SetSRID(geom,4326),3826)"
        sql = """
            select eventid as id,disastername as name,county,town,vill,photodate,photoangle,description,note,disasteryear,disastername,filename,
            ST_AsGeoJson(ST_SetSRID(geom,4326))::json as geom
            from history_photo_swcb where lat > -90 and lat < 90 and
            ST_DWithin(%s,%s, %d);
        """ % (pt,geom,radius)

        rows = db.engine.execute(sql).fetchall()
        if len(rows) == 0:
            return {"error": "範圍內無歷史影像資料"}
        arr = []
        for row in rows:
            d = dict(row)
            d["geom"] = d["geom"]
            d["popup"] = {
                "title": d["name"],
                "photo": d["filename"],
                "desc":d["description"]
            }
            arr.append(d)

        geom = MergeRowsToGeoJson(arr,idKey="id",skipArr=["geom"])

        data = {}
        data["geom"] = geom
        data["layer"] = SymbolStyle("marker-red",allowOverlap=True)
        if "format" in param and param["format"] == "geojson":
            return geom
        return {
            "nodeID":rows[0]["id"],
            "nodeName":rows[0]["name"],
            "data":[data]
        }

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