from sqlalchemy.sql.functions import func
from model.db import db
from model.river import River
import json

class RiverController():
    def GetRiverGeomOrm(self):
        r = db.session.query(func.ST_AsGeoJSON(River.wkb_geometry).label("geom")).first()
        return json.loads(r.geom)

    def GetRiverGeomSQL(self):
        sql = "select ogc_fid,ST_AsGeoJson(wkb_geometry) as geom from c1300 limit 1;"
        result = db.engine.execute(sql)
        r = dict(result.first())
        return json.loads(r["geom"])