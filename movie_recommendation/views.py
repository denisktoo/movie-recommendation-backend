from rest_framework.response import Response
from rest_framework import viewsets, permissions, mixins, status, generics
from .models import (
    User, Favorite, Watchlist, Rating, SearchHistory
    , RecommendationCache
)
from .serializer import (
    RegisterSerializer, UserSerializer, MovieSerializer, FavoriteSerializer, WatchlistSerializer
    , RatingSerializer, SearchHistorySerializer, RecommendationCacheSerializer
)
from .permissions import IsAdminUser, IsOwnerOrAdmin
from .tmdb import fetch_and_cache_trending_movies
from django_filters.rest_framework import DjangoFilterBackend
from .filter import MovieFilter
from rest_framework.decorators import action
from .recommendation_service import (
    recommend_from_search_history,
    recommend_from_ratings,
)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsOwnerOrAdmin]

    # def perform_update(self, serializer):
    #     if self.request.user.role != 'admin':
    #         # Force role to remain unchanged
    #         serializer.save(role=self.get_object().role)
    #     else:
    #         serializer.save()

    def perform_update(self, serializer):
        if self.request.user.role == 'admin':
            # Admin can change role
            serializer.save(allow_role_change=True)
        else:
            # Normal users cannot change role
            serializer.save(role=self.get_object().role)

class MovieViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = MovieSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_class = MovieFilter

    def get_queryset(self):
        return fetch_and_cache_trending_movies()

class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [IsOwnerOrAdmin]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class WatchlistViewSet(viewsets.ModelViewSet):
    serializer_class = WatchlistSerializer
    permission_classes = [IsOwnerOrAdmin]

    def get_queryset(self):
        return Watchlist.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class RatingViewSet(viewsets.ModelViewSet):
    serializer_class = RatingSerializer
    permission_classes = [IsOwnerOrAdmin]

    def get_queryset(self):
        return Rating.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class SearchHistoryViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = SearchHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SearchHistory.objects.filter(user=self.request.user).order_by('-searched_at')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['delete'])
    def clear(self, request):
        self.get_queryset().delete()
        return Response({"message": "Search history cleared"}, status=status.HTTP_204_NO_CONTENT)

class RecommendationCacheViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RecommendationCacheSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return RecommendationCache.objects.filter(user=self.request.user)

class RecommendationViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='from-search-history')
    def from_search_history(self, request):
        movies = recommend_from_search_history(request.user, limit=10)
        serializer = MovieSerializer(movies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='from-ratings')
    def from_ratings(self, request):
        movies = recommend_from_ratings(request.user, limit=10)
        serializer = MovieSerializer(movies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
