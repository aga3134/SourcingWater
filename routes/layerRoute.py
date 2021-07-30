from flask import Blueprint, render_template, current_app, jsonify,request
from controller.layerController import LayerController

layerRoute = Blueprint("layerRoute", __name__)

@layerRoute.route("/basin", methods=["GET"])
def basin():
    lc = LayerController()
    data = lc.GetBasin()
    return jsonify(data)

@layerRoute.route("/rainStation", methods=["GET"])
def rainStation():
    lc = LayerController()
    data = lc.GetRainStation()
    return jsonify(data)
