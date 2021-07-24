from flask import Flask, redirect, render_template, request, session, url_for
from cs50 import SQL
from flask_session import Session
from tempfile import mkdtemp

import api.api as api
import helpers as h

app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///application.db")

from .auth.auth import auth_bp
from .general.general import general_bp
from .user.user import user_bp

app.register_blueprint(auth_bp)
app.register_blueprint(general_bp)
app.register_blueprint(user_bp)


@app.route("/search")
def search():
    """Basic search by title, can take category filters"""
    # Assignment and checks
    title = request.args.get("title")
    filters = request.args.get("filter")

    if not title:
        return render_template("search.html", error="Please submit a valid search")

    results = api.global_search(title, filters)

    return render_template("search.html",
                           movies=results["movie"],
                           series=results["tv"],
                           people=results["person"])


@app.route("/details/<media_type>/<media_id>")
def details(media_type, media_id):
    if not media_id or not media_type:
        return render_template("search.html", error="Please submit a valid search")

    query = api.query_by_id(media_id, media_type)

    if query is None:
        return render_template("search.html", error="Please submit a valid search")

    results = api.parse_query_by_id(query, media_type)

    return render_template("details.html",
                           media=results["media"],
                           seasons=results["seasons"],
                           actors=results["actors"],
                           recommendations=results["recommendations"],
                           videos=results["videos"],
                           cast=results["cast"])


@app.route("/details/tv/<tv_id>/season/<season_number>/episode/<episode_number>")
def episode_details(tv_id, season_number, episode_number):
    if not tv_id or not season_number or not episode_number:
        return render_template("search.html", error="Please submit a valid search")
    media_type = "tv"
    query = api.query_by_id(tv_id, media_type, season_number, episode_number)
    get_episodes = api.query_by_id(tv_id, media_type, season_number)
    episodes = api.parse_episodes(get_episodes)
    results = api.parse_query_by_id(query, media_type)

    return render_template("details.html",
                           media=results["media"],
                           actors=results["actors"],
                           videos=results["videos"],
                           episodes=episodes,
                           tv_id=tv_id,
                           season_number=season_number)


if __name__ == '__main__':
    app.run()
