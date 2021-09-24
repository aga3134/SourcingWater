from sqlalchemy.sql.functions import func
from model.db import db
import json
from controller.util import DictToGeoJsonProp,MergeRowsToGeoJson
import requests

class LogicTopoFactory():
    def FindSewageTreatmentPlant(self,param):
        if not "nodeID" in param:
            return {"error":"no nodeID parameter"}
        nodeID = param["nodeID"]
        if not "nodeName" in param:
            return {"error":"node nodeName parameter"}
        nodeName = param["nodeName"]

        #查工廠座標
        url = "https://egis.moea.gov.tw/MoeaEGFxData_WebAPI_Inside/InnoServe/Factory?resptype=GeoJson&keyword=%s" % (nodeName)
        geom = requests.get(url).json()
        if len(geom["features"]) == 0:
            return {"error":"查無此工廠"}
        coord = geom["features"][0]["geometry"]["coordinates"]
        lng = coord[0]
        lat = coord[1]

        #查工業區範圍
        pt = "ST_SetSRID(ST_POINT(%s,%s),4326)" % (lng,lat)
        geom = "ST_Transform(ST_SetSRID(geom,3826),4326)"
        sql = """
            select fd as id,fname as name,type,catagory,
            %s as geom
            from \"25598-台灣各工業區範圍圖資料集\" where
            ST_Contains(%s,%s);
        """ % (geom,geom,pt)

        row = db.engine.execute(sql).first()
        if row is None:
            return {"error": "查無工業區資料"}
        row = dict(row)

        #查工業區污水處理廠
        #工業區名稱、代碼對不起來，用位置找污水廠
        pt = "ST_Transform(ST_SetSRID(geom,3826),4326)"
        sql = """
            select \"序號\" as id,\"工業區代碼\",\"工業區名稱\" as name,\"所在工業區\",\"地址\",
            ST_AsGeoJson(%s)::json as geom
            from \"8818-工業區污水處理廠分布位置圖\" where
            ST_Contains('%s',%s);
        """ % (pt,row["geom"],pt)
        #print(sql)

        rows = db.engine.execute(sql).fetchall()
        if len(rows) == 0:
            return {"error": "此工業區無污水處理廠資料"}
        arr = []
        for row in rows:
            d = dict(row)
            d["geom"] = d["geom"]
            arr.append(d)
        geom = MergeRowsToGeoJson(arr,idKey="id",skipArr=["geom"])

        data = {}
        data["geom"] = geom
        data["layer"] = [
            {
                "type": "symbol",
                "layout":{
                    "icon-image": "waterin",
                    "text-field": ["get", "name"],
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
            "nodeID":rows[0]["id"],
            "nodeName":rows[0]["name"],
            "data":[data]
        }

    def FindIndustryArea(self,param):
        if not "nodeID" in param:
            return {"error":"no nodeID parameter"}
        nodeID = param["nodeID"]
        if not "nodeName" in param:
            return {"error":"node nodeName parameter"}
        nodeName = param["nodeName"]

        #查工廠位置
        url = "https://egis.moea.gov.tw/MoeaEGFxData_WebAPI_Inside/InnoServe/Factory?resptype=GeoJson&keyword=%s" % (nodeName)
        geom = requests.get(url).json()
        if len(geom["features"]) == 0:
            return {"error":"查無此工廠"}
        coord = geom["features"][0]["geometry"]["coordinates"]
        lng = coord[0]
        lat = coord[1]

        #查工業區範圍
        pt = "ST_SetSRID(ST_POINT(%s,%s),4326)" % (lng,lat)
        geom = "ST_Transform(ST_SetSRID(geom,3826),4326)"
        sql = """
            select fd as id,fname as name,type,catagory,
            ST_AsGeoJson(%s)::json as geom
            from \"25598-台灣各工業區範圍圖資料集\" where
            ST_Contains(%s,%s);
        """ % (geom,geom,pt)

        row = db.engine.execute(sql).first()
        if row is None:
            return {"error": "查無工業區資料"}
        row = dict(row)

        data = {}
        data["geom"] = row["geom"]
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
            "nodeID":row["id"],
            "nodeName":row["name"],
            "data":[data]
        }

    def GetNodeInfo(self,param):
        if not "nodeID" in param:
            return {"error":"no nodeID parameter"}
        nodeID = param["nodeID"]

        return {"error":" 查無基本資料"}