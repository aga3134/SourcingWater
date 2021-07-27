from sqlalchemy.sql.functions import func
from model.db import db
import json

class LogicTopoBasin():
    def FindBasinByID(self,param):
        if not "nodeID" in param:
            return {"error":"no id parameter"}
        nodeID = param["nodeID"]
        sql = "select basin_no,basin_name as title,area,ST_AsGeoJson(ST_Transform(ST_SetSRID(geom,3826),4326)) as geom from basin where basin_name='%s';" % nodeID
        row = dict(db.engine.execute(sql).first())
        row["type"] = "fill"
        row["paint"] = {
            "fill-color":"#ff3333",
            "fill-opacity":0.5
        }
        result = [row]
        return result

    def FindMainRiverByID(self,param):
        if not "nodeID" in param:
            return {"error":"no id parameter"}
        nodeID = param["nodeID"]
        #目前資料庫只有頭前溪主河道，先用這個測試
        sql = "select ogc_fid,ST_AsGeoJson(wkb_geometry) as geom from c1300 limit 1;"
        row = dict(db.engine.execute(sql).first())
        row["title"] = "頭前溪"
        row["type"] = "line"
        row["paint"] = {
            "line-color": "#f33",
            "line-width": 4
        }
        result = [row]
        return result
