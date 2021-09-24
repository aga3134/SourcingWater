from sqlalchemy.sql.functions import func
from model.db import db
import json
from controller.util import DictToGeoJsonProp
import requests

class LogicTopoAgricultureArea():
    def FindAgriculturePollution(self,param):
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

    def FindCrop(self,param):
        if not "nodeID" in param:
            return {"error":"no nodeID parameter"}
        nodeID = param["nodeID"]
        nodeName = ""
        if "nodeName" in param:
            nodeName = param["nodeName"]
        
        sql = "select countyname,townname as id,townname as name from town_moi where townname='%s';" % (nodeID)
        row = db.engine.execute(sql).first()
        if row is None:
            return {"error": "無縣市資料"}
        row = dict(row)

        url = "https://data.coa.gov.tw/Service/OpenData/FromM/TownCropData.aspx?city=%s&town=%s" % (row["countyname"],row["name"])
        #print(url)
        data = requests.get(url).json()
        #print(data)
        chartData = {
            "收穫面積(公頃)":{},
            "種植面積(公頃)":{},
            "每公頃收穫量(公斤)":{},
            "收量(公斤)":{},
        }
        for d in data:
            crop = d["作物"]
            if d["期作"] != "全年":
                continue
            for key in d:
                if key not in chartData:
                    continue
                if crop not in chartData[key]:
                    chartData[key][crop] = d[key]
            
        #print(chartData)
        chartArr = []
        for key in chartData:
            d = chartData[key]
            xArr = []
            yArr = []
            for c in d:
                xArr.append(c)
                yArr.append(d[c])

            chartArr.append({
                "option":{
                    "series": [{
                        "name": key,
                        "data": yArr
                    }],
                    "chart": {
                        "width": "100%",
                        "height": len(xArr)*20,
                        "type": 'bar',
                        "zoom": {
                            "enabled": False
                        }
                    },
                    "plotOptions": {
                        "bar": {
                            "borderRadius": 4,
                            "horizontal": True,
                        }
                    },
                    "dataLabels": {
                        "enabled": False
                    },
                    "stroke": {
                        "curve": 'straight'
                    },
                    "title": {
                        "text": nodeName+"-"+key,
                        "align": 'left'
                    },
                    "grid": {
                        "row": {
                            "colors": ['#f3f3f3', 'transparent'],
                            "opacity": 0.5
                        },
                    },
                    "xaxis": {
                        "labels": {
                            "rotate": -90
                        },
                        "categories": xArr,
                    }
                }
            })

        return {
            "nodeID":nodeID,
            "nodeName":nodeID,
            "chartArr": chartArr
        }

    def GetNodeInfo(self,param):
        if not "nodeID" in param:
            return {"error":"no nodeID parameter"}
        nodeID = param["nodeID"]

        return {"error":" 查無基本資料"}

        