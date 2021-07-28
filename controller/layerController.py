from sqlalchemy.sql.functions import func
from model.db import db
import json

class LayerController():
    def GetBasin(self):
        sql = "select basin_no,basin_name,area,ST_AsGeoJson(ST_Transform(ST_SetSRID(geom,3826),4326)) as geom from basin;"
        rows = db.engine.execute(sql)
        result = [dict(row) for row in rows]
        return result