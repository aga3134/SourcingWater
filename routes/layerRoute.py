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

@layerRoute.route("/floodStation", methods=["GET"])
def floodStation():
    lc = LayerController()
    data = lc.GetFloodStation()
    return jsonify(data)

@layerRoute.route("/commutag", methods=["GET"])
def commutag():
    param = {}
    for key in request.args:
        param[key] = request.args[key]
    lc = LayerController()
    data = lc.GetCommutag(current_app.config["app"]["commutag"],param)
    return jsonify(data)