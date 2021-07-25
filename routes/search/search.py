from flask import Blueprint, render_template,session, redirect, request

import api.api as api

search_bp = Blueprint('search_bp', __name__, template_folder="../../templates", static_folder='../../static')

@search_bp.route("/search")
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


@search_bp.route("/details/<media_type>/<media_id>")
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


@search_bp.route("/details/tv/<tv_id>/season/<season_number>/episode/<episode_number>")
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
