from sqlalchemy.sql.functions import func
from model.db import db
import json
from controller.util import DictToGeoJsonProp,MergeRowsToGeoJson
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

    def FindEPAFactoryBase(self,param):
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

        pt = "ST_Transform(ST_SetSRID(ST_POINT(%s,%s),4326),3826)" % (lng,lat)
        geom = "ST_SetSRID(geom,3826)"
        sql = """
            select \"EmsNo\",\"FacilityName\",\"County\",\"Township\",
            \"FacilityAddress\",\"IndustryAreaName\",\"IndustryName\",
            ST_AsGeoJson(ST_Transform(%s,4326))::json as geom
            from hackathon.e_factory_base
            where ST_DWithin(%s,%s, %d);
        """ % (geom,pt,geom,radius)

        rows = db.engine.execute(sql).fetchall()
        if len(rows) == 0:
            return {"error": "範圍內無環保署列管工廠資料"}
        arr = []
        for row in rows:
            d = dict(row)
            d["geom"] = d["geom"]
            arr.append(d)
        geom = MergeRowsToGeoJson(arr,idKey="EmsNo",skipArr=["geom"])

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
            "nodeID":rows[0]["EmsNo"],
            "nodeName":rows[0]["FacilityName"],
            "data":[data]
        }

    def FindIndustryArea(self,param):
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
        pt = "ST_Transform(ST_SetSRID(ST_POINT(%s,%s),4326),3826)" % (lng,lat)
        geom = "ST_SetSRID(geom,3826)"
        sql = """
            select fd,fname as title,type,catagory,
            ST_AsGeoJson(ST_Transform(%s,4326))::json as geom,
            ST_Distance(%s,%s) as dist
            from \"25598-台灣各工業區範圍圖資料集\" where
            ST_DWithin(%s,%s, %d)
            order by dist;
        """ % (geom,pt,geom,pt,geom,radius)

        rows = db.engine.execute(sql).fetchall()
        if len(rows) == 0:
            return {"error": "範圍內無工業區資料"}
        arr = []
        for row in rows:
            d = dict(row)
            d["geom"] = d["geom"]
            arr.append(d)

        geom = MergeRowsToGeoJson(arr,idKey="fd",skipArr=["geom"])

        data = {}
        data["geom"] = geom
        data["layer"] = [
            {
                "type": "line",
                "paint": {
                    "line-color": "#3f3",
                    "line-width": 4
                }
            }
        ]
        return {
            "nodeID":rows[0]["title"],
            "nodeName":rows[0]["title"],
            "data":[data]
        }

    def FindSewageTreatmentPlant(self,param):
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
        pt = "ST_Transform(ST_SetSRID(ST_POINT(%s,%s),4326),3826)" % (lng,lat)
        geom = "ST_SetSRID(geom,3826)"
        sql = """
            select \"序號\",\"工業區代碼\",\"工業區名稱\",\"所在工業區\",\"地址\",
            ST_AsGeoJson(ST_Transform(%s,4326))::json as geom,
            ST_Distance(%s,%s) as dist
            from \"8818-工業區污水處理廠分布位置圖\" where
            ST_DWithin(%s,%s, %d)
            order by dist;
        """ % (geom,pt,geom,pt,geom,radius)

        rows = db.engine.execute(sql).fetchall()
        if len(rows) == 0:
            return {"error": "範圍內無污水處理廠資料"}
        arr = []
        for row in rows:
            d = dict(row)
            d["geom"] = d["geom"]
            arr.append(d)

        geom = MergeRowsToGeoJson(arr,idKey="序號",skipArr=["geom"])

        data = {}
        data["geom"] = geom
        data["layer"] = [
            {
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
            }
        ]
        return {
            "nodeID":rows[0]["序號"],
            "nodeName":rows[0]["工業區名稱"],
            "data":[data]
        }