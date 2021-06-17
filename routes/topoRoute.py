from flask import Blueprint, render_template, current_app
from sqlalchemy.sql.functions import func
from model.db import db
from sqlalchemy.orm import sessionmaker
from model.river import River
import json

topoRoute = Blueprint("topoRoute", __name__)

@topoRoute.route("/river")
def river():
    #example for orm
    r = db.session.query(func.ST_AsGeoJSON(River.wkb_geometry).label("geom")).first()
    return json.loads(r.geom)

    #example for sql command
    sql = "select ogc_fid,ST_AsGeoJson(wkb_geometry) as geom from c1300_trace_case1 limit 1;"
    result = db.engine.execute(sql)
    r = dict(result.first())
    return json.loads(r["geom"])