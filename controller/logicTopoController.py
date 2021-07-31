from sqlalchemy.sql.functions import func
from model.db import db
import json
from controller.logicTopoBasin import LogicTopoBasin
from controller.logicTopoPlace import LogicTopoPlace

class LogicTopoController():
    def ListKind(self):
        sql = "select * from s_topology_kind"
        rows = db.engine.execute(sql)
        result = [dict(r) for r in rows]
        return result

    def ListTransfer(self,kind=None):
        sql = "select * from s_topology_transfer"
        if kind is not None:
            sql += " where from_類別='%s'" % kind
        rows = db.engine.execute(sql)
        result = [dict(r) for r in rows]
        return result

    def FindNodeByKind(self,param):
        if not "kind" in param:
            return {"error":"no kind parameter"}
        kind = param["kind"]
        if kind == "流域":
            return LogicTopoBasin().FindBasinByID(param)
        elif kind == "地點":
            return LogicTopoPlace().FindVillageByLatLng(param)
        else:
            return {}

    def FindNodeByTransfer(self,param):
        if not "kind" in param:
            return {"error":"no kind parameter"}
        if not "transfer" in param:
            return {"error":"no transfer parameter"}
        kind = param["kind"]
        transfer = param["transfer"]
        if kind == "流域":
            ltb = LogicTopoBasin()
            if transfer == "流域範圍":
                return ltb.FindBasinByID(param)
            elif transfer in ["主要河道","源頭到海洋路徑"]:
                return ltb.FindMainRiverByID(param)
            else:
                return {}
        elif kind == "地點":
            ltp = LogicTopoPlace()
            if transfer == "淨水廠為何":
                return ltp.FindVillageWaterwork(param)
            elif transfer == "取水口為何":
                return ltp.FindVillageWaterin(param)
            else:
                return {}