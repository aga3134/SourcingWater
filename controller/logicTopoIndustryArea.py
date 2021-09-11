from sqlalchemy.sql.functions import func
from model.db import db
import json
from controller.util import DictToGeoJsonProp,MergeRowsToGeoJson
import requests

class LogicTopoIndustryArea():
    def FindSewageTreatmentPlant(self,param):
        if not "nodeID" in param:
            return {"error":"no nodeID parameter"}
        nodeID = param["nodeID"]

        sql = "select fd as id,fname as name,ST_SetSRID(geom,3826) as geom from \"25598-台灣各工業區範圍圖資料集\" where fd='%s';" % (nodeID)
        row = db.engine.execute(sql).first()
        if row is None:
            return {"error":"無此工業區"}

        #工業區名稱、代碼對不起來，用位置找污水廠
        sql = """
            select \"序號\" as id,\"工業區代碼\",\"工業區名稱\" as name,\"所在工業區\",\"地址\",
            ST_AsGeoJson(ST_Transform(ST_SetSRID(geom,3826),4326))::json as geom
            from \"8818-工業區污水處理廠分布位置圖\" where
            ST_Contains('%s',ST_SetSRID(geom,3826));
        """ % (row["geom"])
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

    def FindFactory(self,param):
        if not "nodeID" in param:
            return {"error":"no nodeID parameter"}
        nodeID = param["nodeID"]

        sql = "select fd as id,fname as name,ST_AsGeoJson(ST_Transform(ST_SetSRID(geom,3826),4326))::json as geom from \"25598-台灣各工業區範圍圖資料集\" where fd='%s';" % (nodeID)
        row = db.engine.execute(sql).first()
        if row is None:
            return {"error":"無此工業區"}

        polygon = row["geom"]["coordinates"][0][0]
        coordArr = []
        for pt in polygon:
            coordArr.append(str(pt[0])+" "+str(pt[1]))
        coordStr = ",".join(coordArr)
        #print(coordStr)
        postData = {
            "respType": "geojson",
            "PolygenStr": coordStr
        }
        r = requests.post("https://egis.moea.gov.tw/MoeaEGFxData_WebAPI_Inside/InnoServe/Factory", data = postData)
        geom = r.json()
        if len(geom["features"]) == 0:
            return {"error":"查無工廠資料"}

        for f in geom["features"]:
            f["properties"]["id"] = f["properties"]["FactoryID"]
            f["properties"]["name"] = f["properties"]["FactoryName"]
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
            "nodeID":f["properties"]["id"],
            "nodeName":f["properties"]["name"],
            "data":[data]
        }
