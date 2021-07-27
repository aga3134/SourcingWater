from flask import Blueprint, render_template, current_app, jsonify,request
from controller.logicTopoController import LogicTopoController

logicTopoRoute = Blueprint("logicTopoRoute", __name__)

@logicTopoRoute.route("/kind", methods=["GET"])
def kind():
    ltc = LogicTopoController()
    data = ltc.ListKind()
    return jsonify(data)

@logicTopoRoute.route("/transfer", methods=["GET"])
def transfer():
    kind = request.args.get("kind",default = "地點", type = str)
    ltc = LogicTopoController()
    data = ltc.ListTransfer()
    return jsonify(data)

@logicTopoRoute.route("/findNodeByKind", methods=["GET"])
def findNodeByKind():
    param = {}
    for key in request.args:
        param[key] = request.args[key]
    ltc = LogicTopoController()
    data = ltc.FindNodeByKind(param)
    return jsonify(data)

@logicTopoRoute.route("/findNodeByTransfer", methods=["GET"])
def findNodeByTransfer():
    param = {}
    for key in request.args:
        param[key] = request.args[key]
    ltc = LogicTopoController()
    data = ltc.FindNodeByTransfer(param)
    return jsonify(data)