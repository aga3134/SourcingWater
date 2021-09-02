from sqlalchemy.sql.functions import func
from model.db import db
import json
from controller.logicTopoBasin import LogicTopoBasin
from controller.logicTopoPlace import LogicTopoPlace
from controller.logicTopoWaterwork import LogicTopoWaterwork

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
            return {"error":"not implemented"}

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
            elif transfer in ["所有河道"]:
                return ltb.FindStreams(param)
            else:
                return {"error":"not implemented"}
        elif kind == "生活區域":
            ltp = LogicTopoPlace()
            if transfer == "淨水廠為何":
                return ltp.FindVillageWaterwork(param)
            elif transfer == "取水口為何":
                return ltp.FindVillageWaterin(param)
            else:
                return {"error":"not implemented"}
        elif kind == "淨水場":
            ltww = LogicTopoWaterwork()
            if transfer == "取水口為何":
                return ltww.FindWaterinByID(param)
            elif transfer == "淨水場水質":
                return ltww.FindWaterworkQuality(param)
            else:
                return {"error":"not implemented"}
        else:
            return {"error":"not implemented"}

    def GetNodeInfo(self,param):
        if not "kind" in param:
            return {"error":"no kind parameter"}
        kind = param["kind"]
        return {"error":" 查無基本資料"}
