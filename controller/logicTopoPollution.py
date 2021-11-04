from sqlalchemy.sql.functions import func
from model.db import db
import json
from controller.util import DictToGeoJsonProp,MergeRowsToGeoJson
from controller.style import *
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
                        "fixedRadius": 1000,
                        "layer": CircleStyle()
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

        for (i,f) in enumerate(geom["features"]):
            f["id"] = i
            f["properties"]["id"] = f["properties"]["FactoryID"]
            f["properties"]["name"] = f["properties"]["FactoryName"]
        
        f = geom["features"][0]

        #generate json_def
        data = {
            "geom": geom,
            "layer": SymbolStyle("marker-red",textKey="FactoryName"),
        }
        if "format" in param and param["format"] == "geojson":
            return geom
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
                "info":"請點選要查詢的位置",
                "nodeID":nodeID,
                "nodeName":nodeName,
                "setting":{
                    "shapeConfig":{
                        "type":"circle",
                        "variable": "shape",
                        "fixedRadius": 1000,
                        "layer": CircleStyle()
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
            select \"EmsNo\" as id,\"FacilityName\" as name,\"County\",\"Township\",
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
        geom = MergeRowsToGeoJson(arr,idKey="id",skipArr=["geom"])

        #generate json_def
        data = {
            "geom": geom,
            "layer": SymbolStyle("marker-red"),
        }
        if "format" in param and param["format"] == "geojson":
            return geom
        return {
            "nodeID":rows[0]["id"],
            "nodeName":rows[0]["name"],
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
                "info":"請點選要查詢的位置",
                "nodeID":nodeID,
                "nodeName":nodeName,
                "setting":{
                    "shapeConfig":{
                        "type":"circle",
                        "variable": "shape",
                        "fixedRadius": 1000,
                        "layer": CircleStyle()
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
            select fd as id,fname as name,type,catagory,
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

        geom = MergeRowsToGeoJson(arr,idKey="id",skipArr=["geom"])

        data = {}
        data["geom"] = geom
        data["layer"] = IndustryAreaStyle()
        if "format" in param and param["format"] == "geojson":
            return geom
        return {
            "nodeID":rows[0]["id"],
            "nodeName":rows[0]["name"],
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
                "info":"請點選要查詢的位置",
                "nodeID":nodeID,
                "nodeName":nodeName,
                "setting":{
                    "shapeConfig":{
                        "type":"circle",
                        "variable": "shape",
                        "fixedRadius": 1000,
                        "layer": CircleStyle()
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
            select \"序號\" as id,\"工業區代碼\",\"工業區名稱\" as name,\"所在工業區\",\"地址\",
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

        geom = MergeRowsToGeoJson(arr,idKey="id",skipArr=["geom"])

        data = {}
        data["geom"] = geom
        data["layer"] = SymbolStyle("waterin",allowOverlap=True)
        if "format" in param and param["format"] == "geojson":
            return geom
        return {
            "nodeID":rows[0]["id"],
            "nodeName":rows[0]["name"],
            "data":[data]
        }

    def FindFactoryInFarm(self,param):
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
                        "fixedRadius": 1000,
                        "layer": CircleStyle()
                    }
                }
            }
        shape = json.loads(param["shape"])

        lat = shape["center"][1]
        lng = shape["center"][0]
        radius = shape["radius"]

        url = "http://api.disfactory.tw/api/factories?lng=%f&lat=%f&range=%f" % (lng,lat,radius*0.001)
        #print(url)
        factory = requests.get(url).json()
        #print(factory)
        if len(factory) == 0:
            return {"error":"鄰近範圍查無農地工廠"}

        arr = []
        for d in factory:
            d["geom"] = {
                "type": "Point",
                "coordinates": [float(d["lng"]),float(d["lat"])]
            }
            arr.append(d)
        geom = MergeRowsToGeoJson(arr,idKey="id",skipArr=["geom","lat","lng"])

        #generate json_def
        data = {
            "geom": geom,
            "layer": SymbolStyle("marker-red"),
        }
        if "format" in param and param["format"] == "geojson":
            return geom
        return {
            "nodeID":factory[0]["id"],
            "nodeName":factory[0]["name"],
            "data":[data]
        }

    def FindWaterpRecord(self,param):
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
                        "fixedRadius": 1000,
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
            select \"EMS_NO\" as id,\"FAC_NAME\" as name,
            ST_AsGeoJson(ST_SetSRID(geom,4326))::json as geom
            from hackathon.e_waterp_record where
            \"LET_EAST\" != '' and \"LET_EAST\" != '' and
            \"LET_EAST\"::double precision > -90 and \"LET_EAST\"::double precision < 90 and
            ST_DWithin(%s,%s, %d);
        """ % (pt,geom,radius)

        rows = db.engine.execute(sql).fetchall()
        if len(rows) == 0:
            return {"error": "範圍內無水污染源放流口資料"}
        arr = []
        for row in rows:
            d = dict(row)
            d["geom"] = d["geom"]
            arr.append(d)

        geom = MergeRowsToGeoJson(arr,idKey="id",skipArr=["geom"])

        data = {}
        data["geom"] = geom
        data["layer"] = SymbolStyle("waterin",allowOverlap=True)
        if "format" in param and param["format"] == "geojson":
            return geom
        return {
            "nodeID":rows[0]["id"],
            "nodeName":rows[0]["name"],
            "data":[data]
        }