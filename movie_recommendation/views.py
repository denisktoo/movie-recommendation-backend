from rest_framework.response import Response
from rest_framework import viewsets, permissions, status, generics
from .models import (
    User, Movie, Favorite, Watchlist, Rating, SearchHistory
    , RecommendationCache
)
from .serializer import (
    RegisterSerializer, UserSerializer, MovieSerializer, FavoriteSerializer, WatchlistSerializer
    , RatingSerializer, SearchHistorySerializer, RecommendationCacheSerializer
)
from .permissions import IsAdminUser, IsOwnerOrAdmin
from .tmdb import get_trending_movies

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

class MovieViewSet(viewsets.ViewSet):
    
    def list(self, request, *args, **kwargs):
        trending_movies = get_trending_movies()
        return Response(trending_movies, status=status.HTTP_200_OK)

class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = [IsOwnerOrAdmin]

class WatchlistViewSet(viewsets.ModelViewSet):
    queryset = Watchlist.objects.all()
    serializer_class = WatchlistSerializer
    permission_classes = [IsOwnerOrAdmin]

class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [IsOwnerOrAdmin]

class SearchHistoryViewSet(viewsets.ModelViewSet):
    queryset = SearchHistory.objects.all()
    serializer_class = SearchHistorySerializer
    permission_classes = [IsOwnerOrAdmin]

class RecommendationCacheViewSet(viewsets.ModelViewSet):
    queryset = RecommendationCache.objects.all()
    serializer_class = RecommendationCacheSerializer
    permission_classes = [IsOwnerOrAdmin]

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
