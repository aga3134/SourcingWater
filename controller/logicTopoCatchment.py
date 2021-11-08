from sqlalchemy.sql.functions import func
from model.db import db
import json
from controller.util import DictToGeoJsonProp,InitFlow,MergeRowsToGeoJson
from controller.style import *
from colour import Color

class LogicTopoCatchment():
    def FindCatchmentPollution(self,param):
        if not "nodeID" in param:
            return {"error":"no nodeID parameter"}
        nodeID = param["nodeID"]
        nodeName = ""
        if "nodeName" in param:
            nodeName = param["nodeName"]
        
        return {
            "nodeID":nodeID,
            "nodeName":nodeName,
            "info":"請選擇要觀察哪種類型的污染源"
        }

    def FindRainStation(self,param):
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
                        "fixedRadius": 5000,
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
        sql = """select \"stationID\" as id,name,ST_AsGeoJson(ST_SetSRID(geom,4326))::json as geom
            from r_rain_station where ST_DWithin(%s,%s, %d)
        """ % (pt,geom,radius)
        rows = db.engine.execute(sql).fetchall()
        if len(rows) == 0:
            return {"error": "範圍內無雨量站"}

        arr = []
        for row in rows:
            d = dict(row)
            arr.append(d)
        geom = MergeRowsToGeoJson(arr,idKey="id",skipArr=["geom","lat","lon"])
        
        #generate json_def
        data = {
            "geom": geom,
            "layer": SymbolStyle("rain-station"),
        }
        #print(data)
        if "format" in param and param["format"] == "geojson":
            return geom
        return {
            "nodeID":rows[0]["id"],
            "nodeName":rows[0]["name"],
            "data":[data]
        }

    def FindWaterLevelStation(self,param):
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
                        "fixedRadius": 5000,
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
        sql = """select \"BasinIdentifier\" as id,\"ObservatoryName\" as name,ST_AsGeoJson(ST_SetSRID(geom,4326))::json as geom
            from r_waterlevel_station where ST_DWithin(%s,%s, %d)
        """ % (pt,geom,radius)
        rows = db.engine.execute(sql).fetchall()
        if len(rows) == 0:
            return {"error": "範圍內無河川水位站"}

        arr = []
        for row in rows:
            d = dict(row)
            arr.append(d)
        geom = MergeRowsToGeoJson(arr,idKey="id",skipArr=["geom","lat","lon"])

        #generate json_def
        data = {
            "geom": geom,
            "layer": SymbolStyle("flood-station"),
        }
        #print(data)
        if "format" in param and param["format"] == "geojson":
            return geom
        return {
            "nodeID":rows[0]["id"],
            "nodeName":rows[0]["name"],
            "data":[data]
        }

    def FindFloodStation(self,param):
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
                        "fixedRadius": 5000,
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
        sql = """select _id as id,\"stationName\" as name,ST_AsGeoJson(ST_SetSRID(geom,4326))::json as geom
            from r_flood_station where ST_DWithin(%s,%s, %d)
        """ % (pt,geom,radius)
        rows = db.engine.execute(sql).fetchall()
        if len(rows) == 0:
            return {"error": "範圍內無淹水感測站"}

        arr = []
        for row in rows:
            d = dict(row)
            arr.append(d)
        geom = MergeRowsToGeoJson(arr,idKey="id",skipArr=["geom","lat","lon"])

        #generate json_def
        data = {
            "geom": geom,
            "layer": SymbolStyle("waterlevel-station"),
        }
        #print(data)
        if "format" in param and param["format"] == "geojson":
            return geom
        return {
            "nodeID":rows[0]["id"],
            "nodeName":rows[0]["name"],
            "data":[data]
        }
