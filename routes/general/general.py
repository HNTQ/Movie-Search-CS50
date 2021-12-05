from flask import Blueprint, render_template
import api_client as api

general_bp = Blueprint(
    "general_bp",
    __name__,
    template_folder="../../templates",
    static_folder="../../static",
)


@general_bp.route("/")
def index():
    result = api.get_index_data()
    return result
    return render_template("index.html")
