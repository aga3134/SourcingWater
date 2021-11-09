from sqlalchemy.sql.functions import func
from model.db import db
import json
from controller.util import DictToGeoJsonProp,ToFloat
from controller.style import *
from controller.logicTopoBasin import LogicTopoBasin
from controller.logicTopoCatchment import LogicTopoCatchment
import datetime
import requests
import pytz
#using Asia/Taipei will cause offset to be +0806
#taiwan = pytz.timezone('Asia/Taipei')
taiwan = datetime.timezone(offset = datetime.timedelta(hours = 8))

class LogicTopoFloodStation():
    def FindFloodData(self,param):
        if not "nodeID" in param:
            return {"error":"no id parameter"}
        nodeID = param["nodeID"]

        nodeName = ""
        if "nodeName" in param:
            nodeName = param["nodeName"]

        sql = "select _id as id,\"stationName\" as name,lat,lng from r_flood_station where _id='%s'" % (nodeID)
        row = db.engine.execute(sql).first()
        if row is None:
            return {"error": "無淹水感測站資料"}
        row = dict(row)

        today = datetime.date.today()
        dayStr = today.strftime("%Y-%m-%d")
        url = "https://riverlog.lass-net.org/flood/floodData?date=%s&minLat=%s&maxLat=%s&minLng=%s&maxLng=%s" % (dayStr,row["lat"],row["lat"],row["lng"],row["lng"])
        #print(url)
        result = requests.get(url).json()
        if result["status"] != "ok":
            return {"error": "讀取淹水資料失敗"}
        #print(result)
        data = {"淹水深度(cm)":[]}
        for r in result["data"]:
            if r["stationID"] != nodeID:
                continue
            t = datetime.datetime.strptime(r["time"],"%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=pytz.utc).astimezone(taiwan)
            data["淹水深度(cm)"].append({
                "x": t,
                "y": r["value"]
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
            "nodeName":nodeName,
            "chartArr": chartArr
        }

    def FindRainStation(self,param):
        ltc = LogicTopoCatchment()
        return ltc.FindRainStation(param)

    def FindWaterLevelStation(self,param):
        ltc = LogicTopoCatchment()
        return ltc.FindWaterLevelStation(param)

    def FindFloodArea(self,param):
        if not "nodeID" in param:
            return {"error":"no id parameter"}
        nodeID = param["nodeID"]

        sql = "select _id as id,\"stationName\" as name,lat,lng from r_flood_station where _id='%s'" % (nodeID)
        row = db.engine.execute(sql).first()
        if row is None:
            return {"error": "無淹水感測站資料"}
        row = dict(row)

        #取得此站所屬流域
        sql = "select basin_no as id,basin_name as name from basin where ST_Contains(ST_Transform(ST_SetSRID(geom,3826),4326),ST_SetSRID(ST_POINT(%s,%s),4326));;" % (row["lng"],row["lat"])
        row = db.engine.execute(sql).first()
        if row is None:
            return {"error": "無流域資料"}
        row = dict(row)

        ltb = LogicTopoBasin()
        return ltb.FindFloodArea({"nodeID":row["id"],"nodeName":row["name"]})