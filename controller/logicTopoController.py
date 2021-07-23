from sqlalchemy.sql.functions import func
from model.db import db
import json

class LogicTopoController():
    def ListLogicKind(self):
        sql = "select * from s_topology_kind"
        rows = db.engine.execute(sql)
        result = [dict(r) for r in rows]
        return result

    def ListKindTransfer(self,kind):
        sql = "select * from s_topology_transfer where from_類別='%s'" % kind
        rows = db.engine.execute(sql)
        result = [dict(r) for r in rows]
        return result

    def FindNodeByKind(self,kind,param):
        pass
    def FindNodeByTransfer(self,kind,transfer,param):
        pass