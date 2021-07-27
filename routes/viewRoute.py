from flask import Blueprint, render_template, current_app

viewRoute = Blueprint("viewRoute", __name__, template_folder="templates")

@viewRoute.route("/", methods=["GET"])
def home():
    return render_template("index.html",config=current_app.config["app"])