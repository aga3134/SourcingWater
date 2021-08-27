from sqlalchemy.sql.functions import func
from model.db import db
import json
from controller.util import DictToGeoJsonProp

class LogicTopoBasin():
    def FindBasinByID(self,param):
        if not "nodeID" in param:
            return {"error":"no id parameter"}
        nodeID = param["nodeID"]
        sql = "select basin_no,basin_name as title,area,ST_AsGeoJson(ST_Transform(ST_SetSRID(geom,3826),4326))::json as geom from basin where basin_name='%s';" % nodeID
        row = db.engine.execute(sql).first()
        if row is None:
            return {"error": "無流域資料"}
        row = dict(row)

        row["geom"] = DictToGeoJsonProp(row)
        row["layer"] = [
            {
                "type": "line",
                "paint": {
                    "line-color":"#fff",
                    "line-width":3
                }
            }
        ]

        return {
            "nodeID":nodeID,
            "nodeName":nodeID+"流域",
            "data":[row]
        }

    def FindMainRiverByID(self,param):
        if not "nodeID" in param:
            return {"error":"no id parameter"}
        nodeID = param["nodeID"]
        #目前資料庫只有頭前溪主河道，先用這個測試
        sql = "select ogc_fid,ST_AsGeoJson(geom)::json as geom from c1300 limit 1;"
        row = db.engine.execute(sql).first()
        if row is None:
            return {"error": "無主流資料"}
        row = dict(row)
        row["title"] = "頭前溪"

        row["geom"] = DictToGeoJsonProp(row)
        row["layer"] = [
            {
                "type": "line",
                "paint":{
                    "line-color": "#f33",
                    "line-width": 4
                }
            }
        ]
        return {
            "nodeID":nodeID,
            "nodeName":"頭前溪",
            "setting":{
                "pathIndex":0
            },
            "data":[row]
        }
