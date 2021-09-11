from sqlalchemy.sql.functions import func
from model.db import db
import json
from controller.util import DictToGeoJsonProp,ToFloat,InitFlow,MergeRowsToGeoJson
import datetime
from dateutil.relativedelta import *
import math

class LogicTopoWaterin():
    def FindCatchmentByID(self,param):
        if not "nodeID" in param:
            return {"error":"no id parameter"}
        nodeID = param["nodeID"]
        
        nodeName = ""
        if "nodeName" in param:
            nodeName = param["nodeName"]
        
        #取得取水口位置
        sql = "select name,ST_AsGeoJson(ST_Transform(ST_SetSRID(geom,3826),4326))::json as geom from s_waterin_b where name='%s';" % nodeID
        row = db.engine.execute(sql).first()
        if row is None:
            return {"error": "無取水口資料"}
        row = dict(row)
        coord = row["geom"]["coordinates"]

        #取得流域範圍
        lat = coord[1]
        lng = coord[0]
        sql = "select basin_no from basin where ST_Contains(ST_Transform(ST_SetSRID(geom,3826),4326),ST_SetSRID(ST_POINT(%s,%s),4326));" % (lng,lat)
        row = db.engine.execute(sql).first()
        if row is None:
            return {"error": "查無流域資料"}
        row = dict(row)
        basinID = row["basin_no"]
        fd, cx_dict = InitFlow(basinID)
        if fd is None:
            return {"error":"查無流域資料"}

        #取得最近河川點
        streamPt = fd.point_with_streams(coord,dist_min=5000,min_sto=cx_dict["min_sto"])
        if streamPt is None:
            return {"error":"查無最近河川點位"}
        ptArr = [[streamPt[2],streamPt[3],"%s集水區" % nodeName]]
        #ptArr = [[coord[0],coord[1],"%s集水區" % nodeName]]

        #產生集水區
        row = {}
        row["id"] = nodeID
        row["name"] = nodeName+"集水區"
        row["geom"] = json.loads(fd.basins(ptArr,filename=None))
        row["layer"] = [
            {
                "type": "fill",
                "paint":{
                    "fill-color": "#3333ff",
                    "fill-opacity": 0.5
                }
            }
        ]
        return {
            "nodeID":row["id"],
            "nodeName":row["name"],
            "data":[row]
        }

    def FindWaterinQuantity(self,param):
        if not "nodeID" in param:
            return {"error":"no id parameter"}
        nodeID = param["nodeID"]

        sql = "select max(date) as date from s_waterin_qty where waterin='%s';" % nodeID
        endD = db.engine.execute(sql).first()
        endD = dict(endD)["date"]
        if endD is None:
            return {"error": "無取水量資料"}
        startD = endD + relativedelta(years=-1)

        sql="select * from s_waterin_qty where waterin='%s' and date >='%s' and date < '%s' order by date" %(nodeID,startD,endD)
        rows = db.engine.execute(sql).fetchall()
        data = {"取水量":[]}
        for row in rows:
            d = dict(row)
            value = ToFloat(d["qty"])
            #nan轉成json時會錯誤，設為None
            if math.isnan(value):
                value = None
            data["取水量"].append({
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

        sql = "select \"VILLCODE\" from s_village_waterin where \"WATERIN\" = '%s';" % nodeID
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
        data["layer"] = [
            {
                "type": "fill",
                "paint": {
                    "fill-color": "#33f",
                    "fill-opacity": 0.5
                }
            },
            {
                "type": "line",
                "paint": {
                    "line-color": "#fff",
                    "line-width": 2
                }
            }
        ]
        return {
            "nodeID":rows[0]["id"],
            "nodeName":rows[0]["name"],
            "data":[data]
        }
        