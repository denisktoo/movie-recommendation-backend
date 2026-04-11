import requests
from django.conf import settings

BASE_URL = "https://api.themoviedb.org/3"

def get_trending_movies():
    url = f"{BASE_URL}/trending/movie/week?api_key={settings.TMDB_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get('results', [])
    return []