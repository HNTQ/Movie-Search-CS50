"""
All API queries, parsing, and formatting functions are stored in this file
This project use the TMDB API.
"""
import requests
from os import environ

API_KEY = environ.get("API_KEY")

# ///////////////////////////
#  1 - QUERIES AND API CALLS
# ///////////////////////////


# -----------------------------------------------------------
# Api call to get unique media's details
#
# @keyword String,
# @media_type String, Should be movie, tv, or person
# @season_number [String, Is the season number we are looking for]
# @episode_number [String, Is the episode number we are looking for]

# @Return an array of object, if call is successful or null if no result
# -----------------------------------------------------------
def query_by_id(keyword, media_type, season_number=None, episode_number=None):
    _url = ""
    if media_type == "tv":
        if episode_number is not None:
            _url = (
                f"https://api.themoviedb.org/3/{media_type}/{keyword}/season/{season_number}/episode/{episode_number}"
                f"?api_key={API_KEY}&append_to_response=credits,videos"
            )
        elif season_number is not None:
            _url = f"https://api.themoviedb.org/3/{media_type}/{keyword}/season/{season_number}?api_key={API_KEY}"
        else:
            _url = (
                f"https://api.themoviedb.org/3/{media_type}/{keyword}?api_key={API_KEY}"
                f"&append_to_response=credits,videos,recommendations"
            )
    elif media_type == "person":
        _url = (
            f"https://api.themoviedb.org/3/{media_type}/{keyword}?api_key={API_KEY}"
            f"&append_to_response=combined_credits"
        )
    elif media_type == "movie":
        _url = (
            f"https://api.themoviedb.org/3/{media_type}/{keyword}?api_key={API_KEY}"
            f"&append_to_response=credits,videos,recommendations"
        )

    try:
        response = requests.get(_url)
        response.raise_for_status()
    except requests.RequestException:
        return None

    return response.json()


# -----------------------------------------------------------
# Api call to get all related medias
#
# @keyword String,
# @media_type String, Should be movie, tv, or person
# @page [Number | String, As Api returns only 10 results by page we can specify the page we want]

# @Return an array of objects, if call is successful or null if no result
# -----------------------------------------------------------
def query_by_keyword(keyword, media_type, page=1):
    _url = ""
    if media_type:
        _url = f"https://api.themoviedb.org/3/search/{media_type}?api_key={API_KEY}&query={keyword}&page={page}"
    try:
        response = requests.get(_url)
        response.raise_for_status()
    except requests.RequestException:
        return None

    return response.json()


# ////////////////////////////////
#  2 - PARSING AND FORMATTING DATA
# ////////////////////////////////


# -----------------------------------------------------------
# Will return the data used in search movie for the query by keyword
#
# @response Object,
# @media_type String, Should be movie, tv, or person.

# @Return an array of objects, if call is successful or null
# -----------------------------------------------------------
def parse_query_by_keyword(response, media_type):
    parsed_response = {"movie": [], "tv": [], "person": []}

    if not response:
        return response

    for result in response["results"]:
        if media_type == "movie":
            movie_dict = _media_template(result)

            movie_dict["release_date"] = (
                result["release_date"] if "release_date" in result else ""
            )

            parsed_response["movie"].append(movie_dict)
        elif media_type == "tv":
            series_dict = _media_template(result)
            parsed_response["tv"].append(series_dict)
        elif media_type == "person":
            actors_dict = {
                "id": result["id"],
                "name": result["name"],
                "profile_path": result["profile_path"],
                "popularity": result["popularity"],
            }

            parsed_response["person"].append(actors_dict)
    return parsed_response


# -----------------------------------------------------------
# Will return the data used in search movie for the query by id
#
# @response Object,
# @media_type String, Should be movie, tv, or person.

# @Return an array of objects, if call is successful or null
# -----------------------------------------------------------
def parse_query_by_id(response, media_type):
    """Will return the data used in search movie for the query by id"""

    parsed_response = {
        "media": {},
        "actors": [],
        "recommendations": [],
        "videos": [],
        "seasons": [],
        "cast": [],
    }

    if not response or not media_type:
        return parsed_response

    _media_dict = _media_template(response)
    if media_type == "movie":
        _media_dict["release_date"] = response["release_date"]
    parsed_response["media"] = _media_dict

    if "recommendations" in response:
        for recommendation in response["recommendations"]["results"]:
            recommendations_dict = _media_template(recommendation)
            if "movie" in recommendation["media_type"]:
                recommendations_dict["release_date"] = recommendation["release_date"]
            parsed_response["recommendations"].append(recommendations_dict)

    if "videos" in response:
        for video in response["videos"]["results"]:
            videos_dict = {
                "name": video["name"],
                "key": video["key"],
                "site": video["site"],
            }
            parsed_response["videos"].append(videos_dict)

    if "credits" in response:
        _count = 0
        for actor in response["credits"]["cast"]:
            if _count < 10:
                actors_dict = {
                    "id": actor["id"],
                    "name": actor["name"],
                    "character": actor["character"],
                    "profile_path": actor["profile_path"],
                }
                parsed_response["actors"].append(actors_dict)
                _count += 1
            else:
                break

    if "seasons" in response:
        for season in response["seasons"]:
            season_dict = _media_template(season)
            season_dict["season_number"] = season["season_number"]
            episodes = query_by_id(response["id"], media_type, season["season_number"])
            season_dict["episodes"] = parse_episodes(episodes)
            parsed_response["seasons"].append(season_dict)

    if "combined_credits" in response:
        for cast in response["combined_credits"]["cast"]:
            cast_dict = _media_template(cast)
            parsed_response["cast"].append(cast_dict)

    return parsed_response


# -----------------------------------------------------------
# Will return the data used in search movie for the episodes query
#
# @response Object,

# @Return an array of objects, if call is successful or null
# -----------------------------------------------------------
def parse_episodes(response):
    parsed_response = []
    for episode in response["episodes"]:
        episodes_dict = _media_template(episode)
        episodes_dict["episode_number"] = episode["episode_number"]
        parsed_response.append(episodes_dict)
    return parsed_response


# ////////////////////////////////
#  3 - HELPERS
# ////////////////////////////////


# -----------------------------------------------------------
# Create the main object used in Search Movie
#
# @r Object, the response from the api call

# @Return an array of objects
# -----------------------------------------------------------
def _media_template(r):
    return {
        "id": r["id"],
        "title": r["original_title"]
        if "original_title" in r
        else r["title"]
        if "title" in r
        else r["original_name"]
        if "original_name" in r
        else r["name"]
        if "name" in r
        else "",
        "poster_path": r["profile_path"]
        if "profile_path" in r
        else r["poster_path"]
        if "poster_path" in r
        else r["still_path"]
        if "still_path" in r
        else "",
        "backdrop_path": r["backdrop_path"] if "backdrop_path" in r else "",
        "overview": r["overview"]
        if "overview" in r
        else r["biography"]
        if "biography" in r
        else "",
        "media_type": r["media_type"] if "media_type" in r else "",
        "vote_average": r["vote_average"] if "vote_average" in r else "",
    }


def global_search(title, filters):
    medias = {"movie": [], "tv": [], "person": []}

    # Corresponding Api request
    if filters:
        filters = filters.split()
        for filter in filters:
            query = query_by_keyword(title, filter)
            medias[filter] = parse_query_by_keyword(query, filter)[filter]
    else:
        for media in medias:
            query = query_by_keyword(title, media)
            medias[media] = parse_query_by_keyword(query, media)[media]

    return medias
