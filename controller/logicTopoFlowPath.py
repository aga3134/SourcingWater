from sqlalchemy.sql.functions import func
from model.db import db
import json
from controller.util import DictToGeoJsonProp,InitFlow
from controller.style import *

class LogicTopoFlowPath():
    def FindUpstreamCatchment(self,param):
        if not "nodeID" in param:
            return {"error":"no id parameter"}
        nodeID = param["nodeID"]
        fd, cx_dict = InitFlow(nodeID)
        if fd is None:
            return {"error":"查無河道資料"}
        if "sto" in param:
            sto = int(param["sto"])
        else:
            sto = cx_dict['min_sto']

        #shape資訊不完整
        if not "shape" in param:
            return {
                "info":"請點擊河道上一個位置",
                "nodeID":nodeID,
                "nodeName":cx_dict["basin_name"],
                "setting":{
                    "shapeConfig":{
                        "type":"point",
                        "variable": "shape",
                        "num": 1,
                        "layer":SymbolStyle("marker-red",allowOverlap=True)
                    }
                }
            }
        shape = json.loads(param["shape"])
        #add dummy name for each point
        for pt in shape["ptArr"]:
            pt.append("")
        #print(shape)

        row = {}
        row["id"] = nodeID
        row["name"] = cx_dict["basin_name"]+"上游集水區"
        row["geom"] = json.loads(fd.basins(shape["ptArr"],filename=None))
        row["layer"] = SubbasinStyle()
        if "format" in param and param["format"] == "geojson":
            return row["geom"]
        return {
            "nodeID":row["id"],
            "nodeName":row["name"],
            "data":[row]
        }
        
    def FindDownstreamPath(self,param):
        if not "nodeID" in param:
            return {"error":"no id parameter"}
        nodeID = param["nodeID"]
        fd, cx_dict = InitFlow(nodeID)
        if fd is None:
            return {"error":"查無河道資料"}
        if "sto" in param:
            sto = int(param["sto"])
        else:
            sto = cx_dict['min_sto']

        #shape資訊不完整
        if not "shape" in param:
            return {
                "info":"請點擊河道上一個位置",
                "nodeID":nodeID,
                "nodeName":cx_dict["basin_name"],
                "setting":{
                    "shapeConfig":{
                        "type":"point",
                        "variable": "shape",
                        "num": 1,
                        "layer":SymbolStyle("marker-red",allowOverlap=True)
                    }
                }
            }
        shape = json.loads(param["shape"])
        #add dummy name for each point
        for pt in shape["ptArr"]:
            pt.append("")
        #print(shape)

        row = {}
        row["id"] = nodeID
        row["name"] = cx_dict["basin_name"]+"下游入海線"
        row["geom"] = json.loads(fd.path(shape["ptArr"],filename=None))
        row["layer"] = FlowPathStyle(lineWidth=2,color="#3f3")
        if "format" in param and param["format"] == "geojson":
            return row["geom"]
        return {
            "nodeID":row["id"],
            "nodeName":row["name"],
            "data":[row]
        }

    def FindBasin(self,param):
        if not "nodeID" in param:
            return {"error":"no id parameter"}
        nodeID = param["nodeID"]
        sql = "select basin_no as id,basin_name as name,area,ST_AsGeoJson(ST_Transform(ST_SetSRID(geom,3826),4326))::json as geom from basin where basin_no='%s';" % nodeID
        row = db.engine.execute(sql).first()
        if row is None:
            return {"error": "無流域資料"}
        row = dict(row)

        row["geom"] = DictToGeoJsonProp(row)
        row["layer"] = BasinStyle(lineWidth=3)
        if "format" in param and param["format"] == "geojson":
            return row["geom"]
        return {
            "nodeID":row["id"],
            "nodeName":row["name"],
            "data":[row]
        }

    def BirdView(self,param):
        if not "nodeID" in param:
            return {"error":"no id parameter"}
        nodeID = param["nodeID"]
        nodeName = ""
        if "nodeName" in param:
            nodeName = param["nodeName"]

        row = {}
        row["id"] = nodeID
        row["name"] = nodeName
        #使用上個quest的流路當路徑，這邊geom先設空座標
        row["geom"] = {
            "type":"FeatureCollection",
            "features":[]
        }
        row["layer"] = FlowPathStyle(lineWidth=2,color="#33f")
        return {
            "nodeID":row["id"],
            "nodeName":row["name"],
            "setting":{
                "pathIndex":0
            },
            "data":[row]
        }
