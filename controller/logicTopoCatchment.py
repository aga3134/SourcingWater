from sqlalchemy.sql.functions import func
from model.db import db
import json
from controller.util import DictToGeoJsonProp,ToFloat,InitFlow
import datetime
from dateutil.relativedelta import *
import math

class LogicTopoCatchment():
    def FindCatchmentPollution(self,param):
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