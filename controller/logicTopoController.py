from sqlalchemy.sql.functions import func
from model.db import db
import json
from controller.logicTopoBasin import LogicTopoBasin
from controller.logicTopoLivingArea import LogicTopoLivingArea
from controller.logicTopoAgricultureArea import LogicTopoAgricultureArea
from controller.logicTopoWaterwork import LogicTopoWaterwork
from controller.logicTopoWaterin import LogicTopoWaterin
from controller.logicTopoFlowPath import LogicTopoFlowPath
from controller.logicTopoCatchment import LogicTopoCatchment
from controller.logicTopoPollution import LogicTopoPollution
from controller.logicTopoIndustryArea import LogicTopoIndustryArea
from controller.logicTopoFactory import LogicTopoFactory
from controller.logicTopoSewageTreatmentPlant import LogicTopoSewageTreatmentPlant

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
            elif transfer == "農業區域":
                return ltb.FindAgricultureArea(param)
            elif transfer == "工業區域":
                return ltb.FindIndustryArea(param)
            elif transfer in ["雨水下水道","污水下水道","圳路"]:
                return {"error":"無開放資料"}
        elif kind == "流路":
            ltfp = LogicTopoFlowPath()
            if transfer == "上游集水區":
                return ltfp.FindUpstreamCatchment(param)
            elif transfer == "下游入海線":
                return ltfp.FindDownstreamPath(param)
            elif transfer == "所屬流域":
                return ltfp.FindBasin(param)
            elif transfer == "鳥覽流路":
                return ltfp.BirdView(param)
        elif kind == "生活區域":
            ltla = LogicTopoLivingArea()
            if transfer == "淨水廠為何":
                return ltla.FindVillageWaterwork(param)
            elif transfer == "水源在哪":
                return ltla.FindVillageWaterin(param)
            elif transfer == "有哪些污染源":
                return ltla.FindVillagePollution(param)
            elif transfer == "用水統計(三級經濟區)":
                return ltla.FindWaterUse(param)
        elif kind == "農業區域":
            ltaa = LogicTopoAgricultureArea()
            if transfer == "有哪些污染源":
                return ltaa.FindAgriculturePollution(param)
            elif transfer == "有哪些農作物":
                return ltaa.FindCrop(param)
        elif kind == "淨水場":
            ltww = LogicTopoWaterwork()
            if transfer == "取水口為何":
                return ltww.FindWaterinByID(param)
            elif transfer == "淨水場水質":
                return ltww.FindWaterworkQuality(param)
            elif transfer == "淨水場供水量":
                return ltww.FindWaterworkQuantity(param)
            elif transfer == "供給哪些區域":
                return ltww.FindSupplyLivingArea(param)
        elif kind == "取水口":
            ltwi = LogicTopoWaterin()
            if transfer == "集水區為何":
                return ltwi.FindCatchmentByID(param)
            elif transfer == "取水量":
                return ltwi.FindWaterinQuantity(param)
            elif transfer == "生活供給範圍":
                return ltwi.FindSupplyLivingArea(param)
        elif kind == "集水區":
            ltc = LogicTopoCatchment()
            if transfer == "有哪些污染源":
                return ltc.FindCatchmentPollution(param)
        elif kind == "鄰近污染源":
            ltp = LogicTopoPollution()
            if transfer == "工廠":
                return ltp.FindFactory(param)
            elif transfer == "環境保護列管對象":
                return ltp.FindEPAFactoryBase(param)
            elif transfer == "工業區域":
                return ltp.FindIndustryArea(param)
            elif transfer == "工業污水處理廠":
                return ltp.FindSewageTreatmentPlant(param)
            elif transfer == "農地工廠":
                return ltp.FindFactoryInFarm(param)
        elif kind == "工業區域":
            ltia = LogicTopoIndustryArea()
            if transfer == "哪個污水廠":
                return ltia.FindSewageTreatmentPlant(param)
            elif transfer == "有哪些工廠":
                return ltia.FindFactory(param)
        elif kind == "工廠":
            ltf = LogicTopoFactory()
            if transfer == "哪個污水廠":
                return ltf.FindSewageTreatmentPlant(param)
            elif transfer == "屬於哪個工業區":
                return ltf.FindIndustryArea(param)
        elif kind == "工業污水處理廠":
            ltstp = LogicTopoSewageTreatmentPlant()
            if transfer == "處理範圍":
                return ltstp.FindProcessingArea(param)

        return {"error":"not implemented"}

    def GetNodeInfo(self,param):
        if not "kind" in param:
            return {"error":"no kind parameter"}
        kind = param["kind"]
        if not "nodeID" in param:
            return {"error":"no nodeID parameter"}
        nodeID = param["nodeID"]

        if kind == "流域":
            return LogicTopoBasin().GetNodeInfo(param)
        elif kind == "流路":
            return LogicTopoFlowPath().GetNodeInfo(param)
        elif kind == "生活區域":
            return LogicTopoLivingArea().GetNodeInfo(param)
        elif kind == "農業區域":
            return LogicTopoAgricultureArea().GetNodeInfo(param)
        elif kind == "淨水場":
            return LogicTopoWaterwork().GetNodeInfo(param)
        elif kind == "取水口":
            return LogicTopoWaterin().GetNodeInfo(param)
        elif kind == "集水區":
            return LogicTopoCatchment().GetNodeInfo(param)
        elif kind == "鄰近污染源":
            return LogicTopoPollution().GetNodeInfo(param)
        elif kind == "工業區域":
            return LogicTopoIndustryArea().GetNodeInfo(param)
        elif kind == "工廠":
            return LogicTopoFactory().GetNodeInfo(param)
        elif kind == "工業污水處理廠":
            return LogicTopoSewageTreatmentPlant().GetNodeInfo(param)
        return {"error":" 查無基本資料"}
