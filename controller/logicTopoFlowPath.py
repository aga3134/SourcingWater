from sqlalchemy.sql.functions import func
from model.db import db
import json
from controller.util import DictToGeoJsonProp,InitFlow

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
                        "layer":{
                            "type": "symbol",
                            "layout":{
                                "icon-image": "marker-red",
                                "icon-allow-overlap": True,
                                "text-allow-overlap": True
                            }
                        }
                    }
                }
            }
        shape = json.loads(param["shape"])
        #add dummy name for each point
        for pt in shape["ptArr"]:
            pt.append("")
        #print(shape)

        row = {}
        row["title"] = cx_dict["basin_name"]+"上游集水區"
        row["geom"] = json.loads(fd.basins(shape["ptArr"],filename=None))
        row["layer"] = [
            {
                "type": "fill",
                "paint":{
                    "fill-color": "#3333ff",
                    "fill-opacity": 0.5
                }
            }
        ]
        return {
            "nodeID":nodeID,
            "nodeName":cx_dict["basin_name"],
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
                        "layer":{
                            "type": "symbol",
                            "layout":{
                                "icon-image": "marker-red",
                                "icon-allow-overlap": True,
                                "text-allow-overlap": True
                            }
                        }
                    }
                }
            }
        shape = json.loads(param["shape"])
        #add dummy name for each point
        for pt in shape["ptArr"]:
            pt.append("")
        #print(shape)

        row = {}
        row["title"] = cx_dict["basin_name"]+"下游入海線"
        row["geom"] = json.loads(fd.path(shape["ptArr"],filename=None))
        row["layer"] = [
            {
                "type": "line",
                "paint":{
                    "line-color": "#3f3",
                    "line-width": 2
                }
            }
        ]
        return {
            "nodeID":nodeID,
            "nodeName":cx_dict["basin_name"],
            "data":[row]
        }