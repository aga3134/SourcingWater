from sqlalchemy.sql.functions import func
from model.db import db
import json
from controller.util import DictToGeoJsonProp,ToFloat,MergeRowsToGeoJson
from controller.style import *
import datetime
from dateutil.relativedelta import *
import math

class LogicTopoWaterwork():
    def FindWaterworkByID(self,param):
        if not "nodeID" in param:
            return {"error":"no id parameter"}
        nodeID = param["nodeID"]

        sql = "select 淨水場名稱 as id,淨水場名稱 as name,主要供水轄區,原水來源,ST_AsGeoJson(ST_Transform(ST_SetSRID(geom,3826),4326))::json as geom from m_waterwork_area where \"淨水場名稱\"='%s';" % nodeID
        row = db.engine.execute(sql).first()
        if row is None:
            return {"error": "無淨水廠資料"}
        row = dict(row)
        
        row["geom"] = DictToGeoJsonProp(row)
        row["layer"] = SymbolStyle("waterwork",allowOverlap=True)
        return {
            "nodeID":row["id"],
            "nodeName":row["name"],
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

        sql = "select name as id,name,ST_AsGeoJson(ST_Transform(ST_SetSRID(geom,3826),4326))::json as geom from s_waterin_b where name='%s';" % v["WATERIN"]
        row = db.engine.execute(sql).first()
        if row is None:
            return {"error": "無取水口資料"}
        row = dict(row)
        
        row["geom"] = DictToGeoJsonProp(row)
        row["layer"] = SymbolStyle("waterin",allowOverlap=True)
        return {
            "nodeID":row["id"],
            "nodeName":row["name"],
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

    def FindSupplyLivingArea(self,param):
        if not "nodeID" in param:
            return {"error":"no id parameter"}
        nodeID = param["nodeID"]

        sql = "select \"VILLCODE\" from s_village_waterin where \"WATERWORK\" = '%s';" % nodeID
        rows = db.engine.execute(sql).fetchall()
        if len(rows) is None:
            return {"error": "查無供水區域"}

        vArr = []
        for r in rows:
            r = dict(r)
            vArr.append("'"+r["VILLCODE"]+"'")
        #print(vArr)
        
        sql = "select countyname,townname,villname as id,villname as name,ST_AsGeoJson(ST_Transform(ST_SetSRID(sim_geom,3826),4326))::json as geom from village_moi_121 where villcode in (%s)" % ",".join(vArr)
        rows = db.engine.execute(sql).fetchall()
        if len(rows) == 0:
            return {"error": "查無村里資料"}

        arr = []
        for row in rows:
            d = dict(row)
            d["geom"] = d["geom"]
            arr.append(d)
        geom = MergeRowsToGeoJson(arr,idKey="id",skipArr=["geom"])

        data = {}
        data["geom"] = geom
        data["layer"] = LivingAreaStyle(lineWidth=2,lineColor="#fff",fill=True)
        return {
            "nodeID":rows[0]["id"],
            "nodeName":rows[0]["name"],
            "data":[data]
        }
    
    def GetNodeInfo(self,param):
        if not "nodeID" in param:
            return {"error":"no nodeID parameter"}
        nodeID = param["nodeID"]

        return {"error":" 查無基本資料"}