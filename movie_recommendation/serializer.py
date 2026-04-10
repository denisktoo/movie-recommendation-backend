from rest_framework import serializers
from .models import (
    User, Movie, Favorite, Watchlist, Rating, SearchHistory
    , RecommendationCache
)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role']
        read_only_fields = ['id', 'role']

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ['tmdb_id', 'title', 'poster_path', 'release_date', 'cached_at']

class FavoriteSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    movie = MovieSerializer(read_only=True)

    class Meta:
        model = Favorite
        fields = ['user', 'movie', 'added_at']

class WatchlistSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    movie = MovieSerializer(read_only=True)

    class Meta:
        model = Watchlist
        fields = ['user', 'movie', 'added_at']

class RatingSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    movie = MovieSerializer(read_only=True)

    class Meta:
        model = Rating
        fields = ['user', 'movie', 'rating', 'rated_at']

class SearchHistorySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = SearchHistory
        fields = ['user', 'query', 'searched_at']

class RecommendationCacheSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = RecommendationCache
        fields = ['user', 'data', 'updated_at']
