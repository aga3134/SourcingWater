from flask import Blueprint, render_template, current_app
from controller.riverController import RiverController

riverRoute = Blueprint("riverRoute", __name__)

@riverRoute.route("/river", methods=["GET"])
def river():
    rc = RiverController()
    #data = rc.GetRiverGeomOrm()
    data = rc.GetRiverGeomSQL()
    return data
