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

class LogicTopoWaterLevelStation():
    def FindWaterLevelData(self,param):
        if not "nodeID" in param:
            return {"error":"no id parameter"}
        nodeID = param["nodeID"]

        nodeName = ""
        if "nodeName" in param:
            nodeName = param["nodeName"]

        sql = "select \"BasinIdentifier\" as id,\"ObservatoryName\" as name,lat,lon from r_waterlevel_station where \"BasinIdentifier\"='%s'" % (nodeID)
        row = db.engine.execute(sql).first()
        if row is None:
            return {"error": "無河川水位站資料"}
        row = dict(row)

        today = datetime.date.today()
        dayStr = today.strftime("%Y-%m-%d")
        url = "https://riverlog.lass-net.org/waterlevel/waterlevelData?date=%s&minLat=%s&maxLat=%s&minLng=%s&maxLng=%s" % (dayStr,row["lat"],row["lat"],row["lon"],row["lon"])
        #print(url)
        result = requests.get(url).json()
        if result["status"] != "ok":
            return {"error": "讀取河川水位資料失敗"}
        #print(result)
        data = {"河川水位(m)":[]}
        for r in result["data"]:
            if r["StationIdentifier"] != nodeID:
                continue
            t = datetime.datetime.strptime(r["RecordTime"],"%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=pytz.utc).astimezone(taiwan)
            data["河川水位(m)"].append({
                "x": t,
                "y": r["WaterLevel"]
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

    def FindFloodStation(self,param):
        ltc = LogicTopoCatchment()
        return ltc.FindFloodStation(param)

    def FindFloodArea(self,param):
        if not "nodeID" in param:
            return {"error":"no id parameter"}
        nodeID = param["nodeID"]

        sql = "select \"BasinIdentifier\" as id,\"ObservatoryName\" as name,lat,lon from r_waterlevel_station where \"BasinIdentifier\"='%s'" % (nodeID)
        row = db.engine.execute(sql).first()
        if row is None:
            return {"error": "無河川水位站資料"}
        row = dict(row)

        #取得此站所屬流域
        sql = "select basin_no as id,basin_name as name from basin where ST_Contains(ST_Transform(ST_SetSRID(geom,3826),4326),ST_SetSRID(ST_POINT(%s,%s),4326));;" % (row["lon"],row["lat"])
        row = db.engine.execute(sql).first()
        if row is None:
            return {"error": "無流域資料"}
        row = dict(row)

        ltb = LogicTopoBasin()
        param["nodeID"] = row["id"]
        param["nodeName"] = row["name"]
        return ltb.FindFloodArea(param)