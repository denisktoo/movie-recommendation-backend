import requests
from django.conf import settings
from django.core.cache import cache
from django.utils.dateparse import parse_date

from .models import Movie

BASE_URL = "https://api.themoviedb.org/3"
TRENDING_CACHE_KEY = "trending_movies"
TRENDING_CACHE_TIMEOUT = 600  # 10 minutes


def get_trending_movies():
    url = f"{BASE_URL}/trending/movie/week?api_key={settings.TMDB_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get("results", [])
    return []


def fetch_and_cache_trending_movies():
    # Check if trending movies are already cached
    cached_movies = cache.get(TRENDING_CACHE_KEY)
    if cached_movies is not None:
        return cached_movies

    # Cache miss - fetch from TMDB and update the database
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

    cached_movies = Movie.objects.all().order_by("-cached_at")

    # Store in Redis for 10 minutes
    cache.set(TRENDING_CACHE_KEY, cached_movies, TRENDING_CACHE_TIMEOUT)

    return cached_movies


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
