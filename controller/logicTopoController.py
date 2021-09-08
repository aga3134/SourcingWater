from sqlalchemy.sql.functions import func
from model.db import db
import json
from controller.logicTopoBasin import LogicTopoBasin
from controller.logicTopoLivingArea import LogicTopoLivingArea
from controller.logicTopoWaterwork import LogicTopoWaterwork
from controller.logicTopoFlowPath import LogicTopoFlowPath

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
        elif kind == "淨水場":
            return LogicTopoWaterwork().FindWaterworkByID(param)
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
            elif transfer == "所有河道":
                return ltb.FindStreams(param)
            elif transfer == "流域分區":
                return ltb.FindSubBasins(param)
            elif transfer == "生活區域":
                return ltb.FindLivingArea(param)
            elif transfer in ["雨水下水道","污水下水道","圳路"]:
                return {"error":"無開放資料"}
            else:
                return {"error":"not implemented"}
        elif kind == "流路":
            ltfp = LogicTopoFlowPath()
            if transfer == "上游集水區":
                return ltfp.FindUpstreamCatchment(param)
            elif transfer == "下游入海線":
                return ltfp.FindDownstreamPath(param)
            elif transfer == "所屬流域":
                return ltfp.FindBasin(param)
        elif kind == "生活區域":
            ltla = LogicTopoLivingArea()
            if transfer == "淨水廠為何":
                return ltla.FindVillageWaterwork(param)
            elif transfer == "取水口為何":
                return ltla.FindVillageWaterin(param)
            elif transfer == "有哪些污染源":
                return ltla.FindVillagePollution(param)
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
