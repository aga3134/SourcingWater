from sqlalchemy.sql.functions import func
from model.db import db
import json
from controller.util import DictToGeoJsonProp,ToFloat
import datetime
from dateutil.relativedelta import *
import math

class LogicTopoWaterwork():
    def FindWaterworkByID(self,param):
        if not "nodeID" in param:
            return {"error":"no id parameter"}
        nodeID = param["nodeID"]

        sql = "select 淨水場名稱 as title,主要供水轄區,原水來源,ST_AsGeoJson(ST_Transform(ST_SetSRID(geom,3826),4326))::json as geom from m_waterwork_area where \"淨水場名稱\"='%s';" % nodeID
        row = db.engine.execute(sql).first()
        if row is None:
            return {"error": "無淨水廠資料"}
        row = dict(row)
        
        row["geom"] = DictToGeoJsonProp(row)
        row["layer"] = [{
                "type": "symbol",
                "layout":{
                    "icon-image": "waterwork",
                    "text-field": ["get", "title"],
                    "text-size": 12,
                    "text-offset": [0, 1.25],
                    "text-anchor": "top"
                },
                "paint":{
                    "text-color": "#ff3"
                }
            }]
        return {
            "nodeID":row["title"],
            "nodeName":row["title"],
            "data":[row]
        }

    def FindWaterinByID(self,param):
        if not "nodeID" in param:
            return {"error":"no id parameter"}
        nodeID = param["nodeID"]
        
        sql = "select * from s_village_waterin where \"WATERWORK\" = '%s';" % nodeID
        v = db.engine.execute(sql).first()
        if v is None:
            return {"error": "無取水口資料"}
        v = dict(v)

        sql = "select name as title,ST_AsGeoJson(ST_Transform(ST_SetSRID(geom,3826),4326))::json as geom from s_waterin_b where name='%s';" % v["WATERIN"]
        row = db.engine.execute(sql).first()
        if row is None:
            return {"error": "無取水口資料"}
        row = dict(row)
        
        row["geom"] = DictToGeoJsonProp(row)
        row["layer"] = [{
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
            }]
        return {
            "nodeID":row["title"],
            "nodeName":row["title"],
            "data":[row]
        }

    def FindWaterworkQuality(self,param):
        if not "nodeID" in param:
            return {"error":"no id parameter"}
        nodeID = param["nodeID"]

        sql = "select max(CAST(\"CKDATE\" as date)) as date from hackathon.e_waterwork_q where \"PLANT\"='%s';" % nodeID
        endD = db.engine.execute(sql).first()
        endD = dict(endD)["date"]
        if endD is None:
            return {"error": "無水質資料"}
        startD = endD + relativedelta(years=-1)

        sql = "select \"ITEM\",CAST(\"CKDATE\" as date) as date,\"ITEMVAL\" from hackathon.e_waterwork_q where \"PLANT\"='%s' and CAST(\"CKDATE\" as date) >= '%s' and CAST(\"CKDATE\" as date) <= '%s' order by CAST(\"CKDATE\" as date);" % (nodeID,startD,endD)
        #print(sql)
        rows = db.engine.execute(sql)
        data = {}
        for row in rows:
            d = dict(row)
            if d["ITEM"] not in data:
                data[d["ITEM"]] = []
            value = ToFloat(d["ITEMVAL"])
            #nan轉成json時會錯誤，設為None
            if math.isnan(value):
                value = None
            data[d["ITEM"]].append({
                "x": datetime.datetime.strftime(d["date"],"%Y-%m-%d"),
                "y": value
            })

        chartArr = []
        for key in data:
            d = data[key]
            chartArr.append({
                "option":{
                    "series": [{
                        "name": key,
                        "data": d
                    }],
                    "chart": {
                        "width": "100%",
                        "type": 'line',
                        "zoom": {
                            "enabled": False
                        }
                    },
                    "dataLabels": {
                        "enabled": False
                    },
                    "stroke": {
                        "curve": 'straight'
                    },
                    "title": {
                        "text": key,
                        "align": 'left'
                    },
                    "grid": {
                        "row": {
                            "colors": ['#f3f3f3', 'transparent'],
                            "opacity": 0.5
                        },
                    },
                    "xaxis": {
                        "type": "datetime",
                    }
                }
            })

        return {
            "nodeID":nodeID,
            "nodeName":nodeID,
            "chartArr": chartArr
        }

    def FindWaterworkQuantity(self,param):
        if not "nodeID" in param:
            return {"error":"no id parameter"}
        nodeID = param["nodeID"]

        sql = "select max(date) as date from s_waterwork_qty where waterwork='%s';" % nodeID
        endD = db.engine.execute(sql).first()
        endD = dict(endD)["date"]
        if endD is None:
            return {"error": "無水量資料"}
        startD = endD + relativedelta(years=-1)

        sql="select * from s_waterwork_qty where waterwork='%s' and date >='%s' and date < '%s' order by date" %(nodeID,startD,endD)
        rows = db.engine.execute(sql).fetchall()
        data = {"水量":[]}
        for row in rows:
            d = dict(row)
            value = ToFloat(d["qty"])
            #nan轉成json時會錯誤，設為None
            if math.isnan(value):
                value = None
            data["水量"].append({
                "x": datetime.datetime.strftime(d["date"],"%Y-%m-%d"),
                "y": value
            })

        chartArr = []
        for key in data:
            d = data[key]
            chartArr.append({
                "option":{
                    "series": [{
                        "name": key,
                        "data": d
                    }],
                    "chart": {
                        "width": "100%",
                        "type": 'line',
                        "zoom": {
                            "enabled": False
                        }
                    },
                    "dataLabels": {
                        "enabled": False
                    },
                    "stroke": {
                        "curve": 'straight'
                    },
                    "title": {
                        "text": key,
                        "align": 'left'
                    },
                    "grid": {
                        "row": {
                            "colors": ['#f3f3f3', 'transparent'],
                            "opacity": 0.5
                        },
                    },
                    "xaxis": {
                        "type": "datetime",
                    }
                }
            })

        return {
            "nodeID":nodeID,
            "nodeName":nodeID,
            "chartArr": chartArr
        }
