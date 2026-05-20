import requests
from django.conf import settings
from django.utils.dateparse import parse_date

from .models import Movie

BASE_URL = "https://api.themoviedb.org/3"


def get_trending_movies():
    url = f"{BASE_URL}/trending/movie/week?api_key={settings.TMDB_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get("results", [])
    return []


def fetch_and_cache_trending_movies():
    movies = get_trending_movies()

    for movie in movies:
        Movie.objects.update_or_create(
            tmdb_id=movie["id"],
            defaults={
                "title": movie.get("title"),
                "poster_path": movie.get("poster_path"),
                "release_date": (
                    parse_date(movie.get("release_date"))
                    if movie.get("release_date")
                    else None
                ),
            },
        )

    return Movie.objects.all().order_by("-cached_at")


def search_movies(query):
    url = f"{BASE_URL}/search/movie"
    params = {
        "api_key": settings.TMDB_API_KEY,
        "query": query,
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get("results", [])
    return []


def get_movie_recommendations(tmdb_id):
    url = f"{BASE_URL}/movie/{tmdb_id}/recommendations"
    params = {
        "api_key": settings.TMDB_API_KEY,
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get("results", [])
    return []
