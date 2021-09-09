from sqlalchemy.sql.functions import func
from model.db import db
import json
from controller.util import DictToGeoJsonProp,ToFloat,InitFlow
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
        sql = "select name as title,ST_AsGeoJson(ST_Transform(ST_SetSRID(geom,3826),4326))::json as geom from s_waterin_b where name='%s';" % nodeID
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
        row["title"] = "%s集水區" % nodeName
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
            "nodeID":nodeID,
            "nodeName":row["title"],
            "data":[row]
        }