from flask import Blueprint, render_template

_development_bp = Blueprint(
    "_development_bp",
    __name__,
    template_folder="../../templates",
    static_folder="../../static",
)


@_development_bp.route("/development/ui")
def index():
    return render_template("ui.html")
