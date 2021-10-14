from sqlalchemy.sql.functions import func
from model.db import db
import json
from controller.util import DictToGeoJsonProp
from controller.style import *

class LogicTopoSewageTreatmentPlant():
    def FindProcessingArea(self,param):
        if not "nodeID" in param:
            return {"error":"no nodeID parameter"}
        nodeID = param["nodeID"]

        #查污水廠位置
        #工業區名稱、代碼對不起來，用位置找污水廠
        sql = """
            select \"序號\" as id,\"工業區代碼\",\"工業區名稱\" as name,\"所在工業區\",\"地址\",
            ST_Transform(ST_SetSRID(geom,3826),4326) as geom
            from \"8818-工業區污水處理廠分布位置圖\" where
            \"序號\"='%s';
        """ % (nodeID)

        ia = db.engine.execute(sql).first()
        if ia is None:
            return {"error": "無取污水處理廠資料"}
        ia = dict(ia)

        #查工業區範圍
        pt = ia["geom"]
        geom = "ST_Transform(ST_SetSRID(geom,3826),4326)"
        sql = """
            select fd as id,fname as name,type,catagory,
            ST_AsGeoJson(%s)::json as geom
            from \"25598-台灣各工業區範圍圖資料集\" where
            ST_Contains(%s,'%s');
        """ % (geom,geom,pt)

        row = db.engine.execute(sql).first()
        if row is None:
            return {"error": "查無工業區資料"}
        row = dict(row)

        data = {}
        data["geom"] = DictToGeoJsonProp(row)
        data["layer"] = IndustryAreaStyle()
        return {
            "nodeID":row["id"],
            "nodeName":row["name"],
            "data":[data]
        }
