"""
All API queries, parsing, and formatting functions are stored in this file
This project use the TMD API.
"""
import os
import requests

API_KEY = os.environ.get("API_KEY")


# Queries
def query_by_title(title):
    """Will look for all types"""
    try:
        url = f"https://api.themoviedb.org/3/search/multi?api_key={API_KEY}&query={title}"
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
        "series": []
    }
    if not response:
        return response

    def generic(r):
        return {
            "id": r["id"],
            "poster_path": r["poster_path"],
            "backdrop_path": r["backdrop_path"],
            "overview": r["overview"],
            "media_type": r["media_type"],
            "vote_average": r["vote_average"]
        }

    for result in response["results"]:
        if "movie" in result["media_type"]:
            movie_dict = generic(result)
            movie_dict["title"] = result["original_title"]
            movie_dict["release_date"] = result["release_date"]
            parsed_response["movies"].append(movie_dict)
        elif "tv" in result["media_type"]:
            series_dict = generic(result)
            movie_dict["title"] = result["name"]
            parsed_response["series"].append(series_dict)

    return parsed_response
