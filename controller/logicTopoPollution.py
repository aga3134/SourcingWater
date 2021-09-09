from sqlalchemy.sql.functions import func
from model.db import db
import json
from controller.util import DictToGeoJsonProp
import requests

class LogicTopoPollution():
    def FindFactory(self,param):
        if not "nodeID" in param:
            return {"error":"no nodeID parameter"}
        nodeID = param["nodeID"]
        nodeName = ""
        if "nodeName" in param:
            nodeName = param["nodeName"]

        #shape資訊不完整
        if not "shape" in param:
            return {
                "info":"請點擊要查詢的位置",
                "nodeID":nodeID,
                "nodeName":nodeName,
                "setting":{
                    "shapeConfig":{
                        "type":"circle",
                        "variable": "shape",
                        "layer":{
                            "type": "line",
                            "paint": {
                                "line-color": "#f33",
                                "line-width": 2
                            }
                        }
                    }
                }
            }
        shape = json.loads(param["shape"])
        lat = shape["center"][1]
        lng = shape["center"][0]
        radius = shape["radius"]
        
        url = "https://egis.moea.gov.tw/MoeaEGFxData_WebAPI_Inside/InnoServe/Factory?resptype=GeoJson&x=%f&y=%f&buffer=%d" % (lng,lat,radius)
        #print(url)
        geom = requests.get(url).json()
        #print(geom)
        if len(geom["features"]) == 0:
            return {"error":"鄰近範圍查無工廠"}

        f = geom["features"][0]

        #generate json_def
        data = {
            "geom": geom,
            "layer": [
                {
                    "type": "symbol",
                    "layout":{
                        "icon-image": "marker-red",
                        "text-field": ["get", "FactoryName"],
                        "text-size": 12,
                        "text-offset": [0, 1.25],
                        "text-anchor": "top",
                    },
                    "paint":{
                        "text-color": "#ff3",
                        "text-halo-color": "#000",
                        "text-halo-width":1,
                        "text-halo-blur": 3
                    }
                }
            ],
        }
        return {
            "nodeID":f["properties"]["FactoryID"],
            "nodeName":f["properties"]["FactoryName"],
            "data":[data]
        }