from flask import Blueprint, render_template, current_app, jsonify,request
from controller.logicTopoController import LogicTopoController

logicTopoRoute = Blueprint("logicTopoRoute", __name__)

@logicTopoRoute.route("/kind")
def kind():
    ltc = LogicTopoController()
    data = ltc.ListLogicKind()
    return jsonify(data)

@logicTopoRoute.route("/transfer")
def transfer():
    kind = request.args.get("kind",default = "地點", type = str)
    ltc = LogicTopoController()
    data = ltc.ListKindTransfer(kind)
    return jsonify(data)
