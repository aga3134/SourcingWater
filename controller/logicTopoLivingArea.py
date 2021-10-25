from sqlalchemy.sql.functions import func
from model.db import db
import json
from controller.util import DictToGeoJsonProp
from controller.style import *
import requests
import math
import datetime

class LogicTopoLivingArea():
    def FindVillageByLatLng(self,param):
        if not "lat" in param or not "lng" in param:
            return {"error":"no location parameter"}
        lat = param["lat"]
        lng = param["lng"]
        sql = "select countyname,townname,villname as id, villname as name,ST_AsGeoJson(ST_Transform(ST_SetSRID(sim_geom,3826),4326))::json as geom from village_moi_121 where ST_Contains(ST_Transform(ST_SetSRID(sim_geom,3826),4326),ST_SetSRID(ST_POINT(%s,%s),4326));" % (lng,lat)
        #sql = "select countyname,townname as id, townname as name, ST_AsGeoJson(ST_Transform(ST_SetSRID(sim_geom,3824),4326))::json as geom from town_moi where ST_Contains(ST_Transform(ST_SetSRID(sim_geom,3824),4326),ST_SetSRID(ST_POINT(%s,%s),4326));" % (lng,lat)
        #sql = "select countyname as id, countyname as name, ST_AsGeoJson(ST_Transform(ST_SetSRID(sim_geom,3824),4326))::json as geom from county_moi where ST_Contains(ST_Transform(ST_SetSRID(sim_geom,3824),4326),ST_SetSRID(ST_POINT(%s,%s),4326));" % (lng,lat)
        row = db.engine.execute(sql).first()
        if row is None:
            return {"error": "無村里資料"}
        row = dict(row)

        row["geom"] = DictToGeoJsonProp(row)
        row["layer"] = LivingAreaStyle()
        if "format" in param and param["format"] == "geojson":
            return row["geom"]
        return {
            "nodeID":row["id"],
            "nodeName":row["name"],
            "data":[row]
        }

    def FindVillageWaterwork(self,param):
        if not "nodeID" in param:
            return {"error":"no nodeID parameter"}
        #get waterwork name from village
        nodeID = param["nodeID"]
        sql = "select * from s_village_waterin where \"VILLNAME\" = '%s';" % nodeID
        v = db.engine.execute(sql).first()
        if v is None:
            return {"error": "無淨水廠資料"}
        v = dict(v)
        
        #get water work info
        sql = "select 淨水場名稱 as id,淨水場名稱 as name,主要供水轄區,原水來源,ST_AsGeoJson(ST_Transform(ST_SetSRID(geom,3826),4326))::json as geom from m_waterwork_area where \"淨水場名稱\"='%s';" % v["WATERWORK"]
        row = db.engine.execute(sql).first()
        if row is None:
            return {"error": "無淨水廠資料"}
        row = dict(row)
        
        row["geom"] = DictToGeoJsonProp(row)
        row["layer"] = SymbolStyle("waterwork",allowOverlap=True)
        if "format" in param and param["format"] == "geojson":
            return row["geom"]
        return {
            "nodeID":row["id"],
            "nodeName":row["name"],
            "data":[row]
        }

    def FindVillageWaterin(self,param):
        if not "nodeID" in param:
            return {"error":"no nodeID parameter"}
        #get waterwork name from village
        nodeID = param["nodeID"]
        sql = "select * from s_village_waterin where \"VILLNAME\" = '%s';" % nodeID
        v = db.engine.execute(sql).first()
        if v is None:
            return {"error": "無取水口資料"}
        v = dict(v)
        
        #get water work info
        sql = "select name as id,name,ST_AsGeoJson(ST_Transform(ST_SetSRID(geom,3826),4326))::json as geom from s_waterin_b where name='%s';" % v["WATERIN"]
        row = db.engine.execute(sql).first()
        if row is None:
            return {"error": "無取水口資料"}
        row = dict(row)
        
        row["geom"] = DictToGeoJsonProp(row)
        row["layer"] = SymbolStyle("waterin",allowOverlap=True)
        if "format" in param and param["format"] == "geojson":
            return row["geom"]
        return {
            "nodeID":row["id"],
            "nodeName":row["name"],
            "data":[row]
        }

    def FindVillagePollution(self,param):
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

    def FindWaterUse(self,param):
        if not "nodeID" in param:
            return {"error":"no id parameter"}
        nodeID = param["nodeID"]
        nodeName = ""
        if "nodeName" in param:
            nodeName = param["nodeName"]

        #shape資訊不完整
        if not "shape" in param:
            return {
                "info":"請點選一個位置",
                "nodeID":nodeID,
                "nodeName":nodeName,
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

        lat = shape["ptArr"][0][1]
        lng = shape["ptArr"][0][0]

        url = "https://egis.moea.gov.tw/MoeaEGFxData_WebAPI_Inside/InnoServe/Water/GetPoint?resptype=GeoJson&x=%f&y=%f" % (lng,lat)
        #print(url)
        geom = requests.get(url).json()
        #print(geom)
        if len(geom["features"]) == 0:
            return {"error":"點選位置查無用水統計"}

        row = {}
        row["geom"] = geom
        row["layer"] = StatisticAreaStyle()

        chartData = {"用水統計":[]}
        for d in geom["features"][0]["properties"]:
            print(d)
            d["date"] = str(d["Year"])+"-"+str(d["Month"])
            value = d["PowerSum"]
            #nan轉成json時會錯誤，設為None
            if math.isnan(value):
                value = None
            chartData["用水統計"].append({
                "x": d["date"],
                "y": value
            })

        chartArr = []
        for key in chartData:
            d = chartData[key]
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

        if "format" in param and param["format"] == "geojson":
            return row["geom"]
        return {
            "nodeID":nodeID,
            "nodeName":nodeName,
            "data":[row],
            "chartArr": chartArr
        }
