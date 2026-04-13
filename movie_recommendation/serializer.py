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
    
    def update(self, instance, validated_data):
        validated_data.pop('role', None)  # Block role updates
        return super().update(instance, validated_data)

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'role']
        extra_kwargs = {'password': {'write_only': True}}
        read_only_fields = ['id', 'role']

    def create(self, validated_data):
        validated_data.pop('role', None) # Block role from request
        return User.objects.create_user(**validated_data)

class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ['id', 'tmdb_id', 'title', 'poster_path', 'release_date', 'cached_at']

class FavoriteSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    movie = MovieSerializer(read_only=True)

    class Meta:
        model = Favorite
        fields = ['id', 'user', 'movie', 'added_at']
        read_only_fields = ['id', 'added_at']

class WatchlistSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    movie = MovieSerializer(read_only=True)

    class Meta:
        model = Watchlist
        fields = ['id', 'user', 'movie', 'added_at']
        read_only_fields = ['id', 'added_at']

class RatingSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    movie = MovieSerializer(read_only=True)

    class Meta:
        model = Rating
        fields = ['id', 'user', 'movie', 'rating', 'rated_at']
        read_only_fields = ['id', 'rated_at']

class SearchHistorySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = SearchHistory
        fields = ['id', 'user', 'query', 'searched_at']
        read_only_fields = ['id', 'searched_at']

class RecommendationCacheSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = RecommendationCache
        fields = ['id', 'user', 'data', 'updated_at']
        read_only_fields = ['id', 'updated_at']
