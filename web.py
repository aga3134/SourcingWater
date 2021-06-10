#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, render_template, url_for, request, redirect
import json
import urllib

with open("config.json","r") as json_file:
    data = json_file.read()
    config = json.loads(data)

app = Flask(__name__)
app.secret_key = config["sessionKey"]

#route
@app.route("/")
def home():
    return render_template("index.html",config=config)

if __name__ == "__main__":
    app.run( )