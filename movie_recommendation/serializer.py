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
        fields = ['tmdb_id', 'title', 'poster_path', 'release_date']

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
