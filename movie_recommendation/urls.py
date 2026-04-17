from django.urls import path, include
from rest_framework import routers
from rest_framework_nested.routers import NestedDefaultRouter
from .views import (
    UserViewSet, MovieViewSet, FavoriteViewSet, WatchlistViewSet, RatingViewSet,
    SearchHistoryViewSet, RecommendationCacheViewSet, RecommendationViewSet,
    RegisterView
)

routers = routers.DefaultRouter()
routers.register(r'users', UserViewSet, basename='user')
routers.register(r'movies', MovieViewSet, basename='movie')
routers.register(r'searches', SearchHistoryViewSet, basename='searchhistory')
routers.register(
    r'recommendations', RecommendationCacheViewSet, basename='recommendationcache'
)
routers.register(
    r'generated-recommendations', RecommendationViewSet,
    basename='generated-recommendations'
)

user_favorites = NestedDefaultRouter(routers, r'users', lookup='user')
user_favorites.register(r'favorites', FavoriteViewSet, basename='user-favorites')

user_ratings = NestedDefaultRouter(routers, r'users', lookup='user')
user_ratings.register(r'ratings', RatingViewSet, basename='user-ratings')

user_watchlist = NestedDefaultRouter(routers, r'users', lookup='user')
user_watchlist.register(r'watchlist', WatchlistViewSet, basename='user-watchlist')

urlpatterns = [
    path('', include(routers.urls)),
    path('', include(user_favorites.urls)),
    path('', include(user_ratings.urls)),
    path('', include(user_watchlist.urls)),
    path('register/', RegisterView.as_view(), name='register'),
]
