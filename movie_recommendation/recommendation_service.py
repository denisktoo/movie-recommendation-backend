from collections import Counter

from django.utils.dateparse import parse_date

from .models import (
    Favorite,
    Movie,
    Rating,
    RecommendationCache,
    SearchHistory,
    Watchlist,
)
from .tmdb import get_movie_recommendations, search_movies


def upsert_movie_from_tmdb(movie_data):
    movie, _ = Movie.objects.update_or_create(
        tmdb_id=movie_data["id"],
        defaults={
            "title": movie.get("title") if (movie := movie_data) else None,
            "poster_path": movie_data.get("poster_path"),
            "release_date": (
                parse_date(movie_data.get("release_date"))
                if movie_data.get("release_date")
                else None
            ),
        },
    )
    return movie


def get_user_excluded_movie_ids(user):
    rated_ids = Rating.objects.filter(user=user).values_list("movie_id", flat=True)
    favorite_ids = Favorite.objects.filter(user=user).values_list("movie_id", flat=True)
    watchlist_ids = Watchlist.objects.filter(user=user).values_list(
        "movie_id", flat=True
    )

    return set(rated_ids) | set(favorite_ids) | set(watchlist_ids)


def cache_recommendations(user, cache_type, movies):
    movie_payload = [
        {
            "tmdb_id": movie.tmdb_id,
            "title": movie.title,
            "poster_path": movie.poster_path,
            "release_date": (
                movie.release_date.isoformat() if movie.release_date else None,
            ),
        }
        for movie in movies
    ]

    RecommendationCache.objects.update_or_create(
        user=user,
        cache_type=cache_type,
        defaults={
            "data": {
                "results": movie_payload,
                "count": len(movie_payload),
            }
        },
    )


def recommend_from_search_history(user, limit=10):
    recent_searches = SearchHistory.objects.filter(user=user).order_by("-searched_at")[
        :5
    ]

    if not recent_searches.exists():
        cache_recommendations(user, "search_history", [])
        return []

    keyword_counter = Counter()
    for search in recent_searches:
        words = search.query.lower().split()
        keyword_counter.update(words)

    top_keywords = [word for word, _ in keyword_counter.most_common(5)]

    candidate_movies = []
    seen_tmdb_ids = set()

    for keyword in top_keywords:
        tmdb_results = search_movies(keyword)
        for movie_data in tmdb_results:
            if movie_data["id"] not in seen_tmdb_ids:
                seen_tmdb_ids.add(movie_data["id"])
                movie = upsert_movie_from_tmdb(movie_data)
                candidate_movies.append(movie)

    excluded_ids = get_user_excluded_movie_ids(user)
    filtered_movies = [
        movie for movie in candidate_movies if movie.id not in excluded_ids
    ]

    final_movies = filtered_movies[:limit]
    cache_recommendations(user, "search_history", final_movies)
    return final_movies


def recommend_from_ratings(user, limit=10):
    liked_ratings = Rating.objects.filter(user=user, rating__gte=4).select_related(
        "movie"
    )

    if not liked_ratings.exists():
        cache_recommendations(user, "ratings", [])
        return []

    recommendation_counter = Counter()
    movie_map = {}

    for rating in liked_ratings:
        tmdb_results = get_movie_recommendations(rating.movie.tmdb_id)
        for movie_data in tmdb_results:
            movie = upsert_movie_from_tmdb(movie_data)
            movie_map[movie.tmdb_id] = movie
            recommendation_counter[movie.tmdb_id] += 1

    excluded_ids = get_user_excluded_movie_ids(user)

    ranked_tmdb_ids = [
        tmdb_id
        for tmdb_id, _ in recommendation_counter.most_common()
        if movie_map[tmdb_id].id not in excluded_ids
    ]

    final_movies = [movie_map[tmdb_id] for tmdb_id in ranked_tmdb_ids[:limit]]
    cache_recommendations(user, "ratings", final_movies)
    return final_movies
