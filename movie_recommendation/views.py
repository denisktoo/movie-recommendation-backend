from rest_framework import viewsets, permissions, status
from .models import (
    User, Movie, Favorite, Watchlist, Rating, SearchHistory
    , RecommendationCache
)
from .serializer import (
    UserSerializer, MovieSerializer, FavoriteSerializer, WatchlistSerializer
    , RatingSerializer, SearchHistorySerializer, RecommendationCacheSerializer
)
from .permissions import IsAdminUser, IsUserOrAdmin

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

class MovieViewSet(viewsets.ModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = [IsUserOrAdmin]

class WatchlistViewSet(viewsets.ModelViewSet):
    queryset = Watchlist.objects.all()
    serializer_class = WatchlistSerializer
    permission_classes = [IsUserOrAdmin]

class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [IsUserOrAdmin]

class SearchHistoryViewSet(viewsets.ModelViewSet):
    queryset = SearchHistory.objects.all()
    serializer_class = SearchHistorySerializer
    permission_classes = [IsUserOrAdmin]

class RecommendationCacheViewSet(viewsets.ModelViewSet):
    queryset = RecommendationCache.objects.all()
    serializer_class = RecommendationCacheSerializer
    permission_classes = [IsUserOrAdmin]

class RegisterViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

