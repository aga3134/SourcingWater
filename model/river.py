from flask import current_app
from geoalchemy2 import Geometry
from model.db import db

class River(db.Model):
    __tablename__ = "c1300_trace_case1"
    ogc_fid = db.Column(db.Integer, primary_key=True)
    wkb_geometry = db.Column(Geometry('MultiLineString',4362))
