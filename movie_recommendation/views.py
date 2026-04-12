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
from django.utils.dateparse import parse_date

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

class MovieViewSet(viewsets.ViewSet):
    permission_classes = [IsAdminUser]
    
    def list(self, request, *args, **kwargs):
        # Fetch from TMDB
        trending_movies = get_trending_movies()

        # Save / Update DB (CACHE)
        for movie in trending_movies:
            Movie.objects.update_or_create(
                tmdb_id=movie['id'],
                defaults={
                    'title': movie.get('title'),
                    'poster_path': movie.get('poster_path'),
                    'release_date': parse_date(movie.get('release_date')) if movie.get('release_date') else None
                }
            )
        
        # Query from DB
        queryset = Movie.objects.all().order_by('-cached_at')

        # Serialize
        serializer = MovieSerializer(queryset, many=True)

        # Return clean response
        return Response(serializer.data, status=status.HTTP_200_OK)

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
