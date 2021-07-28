#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask
import json
import urllib
from routes.viewRoute import viewRoute
from routes.riverRoute import riverRoute
from routes.logicTopoRoute import logicTopoRoute
from routes.layerRoute import layerRoute
from model.db import db

with open("config.json","r") as json_file:
    data = json_file.read()
    config = json.loads(data)

app = Flask(__name__)
app.config["app"] = config
app.secret_key = config["sessionKey"]

pg = config["postgres"]
url = "postgresql://{}:{}@{}:{}/{}"  
url = url.format(pg["user"], pg["password"], pg["host"], pg["port"], pg["db"]) 
app.config["SQLALCHEMY_DATABASE_URI"] = url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

#route
app.register_blueprint(viewRoute,url_prefix="")
app.register_blueprint(riverRoute,url_prefix="/river")
app.register_blueprint(logicTopoRoute,url_prefix="/logicTopo")
app.register_blueprint(layerRoute,url_prefix="/layer")

if __name__ == "__main__":
    app.run( )