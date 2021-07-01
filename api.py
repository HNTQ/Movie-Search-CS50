"""
All API queries, parsing, and formatting functions are stored in this file
This project use the TMD API.
"""
import os
import requests

API_KEY = os.environ.get("API_KEY")


# Queries
def query_data(keyword, media_type=None, season_number=None, episode_number=None):
    """Will look for all types"""
    if media_type:
        if media_type == 'tv':
            if episode_number is not None:
                url = f"https://api.themoviedb.org/3/{media_type}/{keyword}/season/{season_number}/episode/{episode_number}" \
                      f"?api_key={API_KEY}&append_to_response=credits,videos"
            elif season_number is not None:
                url = f"https://api.themoviedb.org/3/{media_type}/{keyword}/season/{season_number}?api_key={API_KEY}"
            else:
                url = f"https://api.themoviedb.org/3/{media_type}/{keyword}?api_key={API_KEY}" \
                      f"&append_to_response=credits,videos,recommendations"
        elif media_type == "person":
            url = f"https://api.themoviedb.org/3/{media_type}/{keyword}?api_key={API_KEY}" \
                  f"&append_to_response=combined_credits"
        elif media_type == "movie":
            url = f"https://api.themoviedb.org/3/{media_type}/{keyword}?api_key={API_KEY}" \
                  f"&append_to_response=credits,videos,recommendations"
    else:
        url = f"https://api.themoviedb.org/3/search/multi?api_key={API_KEY}&query={keyword}"

    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return None

    return response.json()


def query_by_search(keyword, filter=None):
    if not filter:
        url = f"https://api.themoviedb.org/3/search/multi?api_key={API_KEY}&query={keyword}"
    else:
        '''TODO: example for movie: https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={keyword}'''
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return None

    return response.json()


def query_media_by_id(keyword, media_type):
    if media_type == "person":
        url = f"https://api.themoviedb.org/3/{media_type}/{keyword}?api_key={API_KEY}" \
              f"&append_to_response=combined_credits"
    else:
        url = f"https://api.themoviedb.org/3/{media_type}/{keyword}?api_key={API_KEY}" \
              f"&append_to_response=credits,videos,recommendations"
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return None

    return response.json()


def query_tv_details(keyword, season_number, episode_number=None):
    if episode_number is not None:
        url = f"https://api.themoviedb.org/3/tv/{keyword}/season/{season_number}/episode/{episode_number}" \
              f"?api_key={API_KEY}&append_to_response=credits,videos"
    else:
        url = f"https://api.themoviedb.org/3/tv/{keyword}/season/{season_number}?api_key={API_KEY}"

    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return None

    return response.json()

# Parse and formats
def parse_query_by_title(response):
    """ Will return the data used in search movie for the query by title"""
    parsed_response = {
        "movies": [],
        "series": [],
        "people": []
    }
    if not response:
        return response

    for result in response["results"]:
        if "movie" in result["media_type"]:
            movie_dict = media_template(result)
            movie_dict["release_date"] = result["release_date"]
            parsed_response["movies"].append(movie_dict)
        elif "tv" in result["media_type"]:
            series_dict = media_template(result)
            parsed_response["series"].append(series_dict)
        elif "person" in result["media_type"]:
            actors_dict = {
                "id": result["id"],
                "name": result["name"],
                "profile_path": result["profile_path"]
            }
            parsed_response["people"].append(actors_dict)
    return parsed_response


def parse_episodes(response):
    parsed_response = []
    for episode in response["episodes"]:
        episodes_dict = media_template(episode)
        episodes_dict["episode_number"] = episode["episode_number"]
        parsed_response.append(episodes_dict)
    return parsed_response


def parse_detail_by_id(response, media_type):
    """ Will return the data used in search movie for the query by id"""
    parsed_response = {
        "media": {},
        "actors": [],
        "recommendations": [],
        "videos": [],
        "seasons": [],
        "cast": []
    }

    if not response or not media_type:
        return parsed_response

    media_dict = media_template(response)
    if media_type == "movie":
        media_dict["release_date"] = response["release_date"]
    parsed_response["media"] = media_dict

    if "recommendations" in response:
        for recommendation in response["recommendations"]["results"]:
            recommendations_dict = media_template(recommendation)
            if "movie" in recommendation["media_type"]:
                recommendations_dict["release_date"] = recommendation["release_date"]
            parsed_response["recommendations"].append(recommendations_dict)

    if "videos" in response:
        for video in response["videos"]["results"]:
            videos_dict = {
                "name": video["name"],
                "key": video["key"],
                "site": video["site"]
            }
            parsed_response["videos"].append(videos_dict)

    if "credits" in response:
        for actor in response["credits"]["cast"]:
            actors_dict = {
                "id": actor["id"],
                "name": actor["name"],
                "character": actor["character"],
                "profile_path": actor["profile_path"]
            }
            parsed_response["actors"].append(actors_dict)

    if "seasons" in response:
        for season in response["seasons"]:
            season_dict = media_template(season)
            season_dict["season_number"] = season["season_number"]
            episodes = query_data(response["id"], media_type, season["season_number"])
            season_dict["episodes"] = parse_episodes(episodes)
            parsed_response["seasons"].append(season_dict)

    if "combined_credits" in response:
        for cast in response["combined_credits"]["cast"]:
            cast_dict = media_template(cast)
            parsed_response["cast"].append(cast_dict)

    return parsed_response


# HELPERS
def media_template(r):
    return {
        "id": r["id"],
        "title": r["original_title"] if "original_title" in r else r["title"] if "title" in r else r["original_name"]
        if "original_name" in r else r["name"] if "name" in r else "",
        "poster_path": r["profile_path"] if "profile_path" in r else r["poster_path"] if "poster_path" in r else
        r["still_path"] if "still_path" in r else "",
        "backdrop_path": r["backdrop_path"] if "backdrop_path" in r else "",
        "overview": r["overview"] if "overview" in r else r["biography"] if "biography" in r else "",
        "media_type": r["media_type"] if "media_type" in r else "",
        "vote_average": r["vote_average"] if "vote_average" in r else ""
    }