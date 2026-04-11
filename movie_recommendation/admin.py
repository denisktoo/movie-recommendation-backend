from django.contrib import admin
from .models import (
    User, Movie, Favorite, Watchlist, Rating, SearchHistory, RecommendationCache
)

admin.site.register(User)
admin.site.register(Movie)
admin.site.register(Favorite)
admin.site.register(Watchlist)
admin.site.register(Rating)
admin.site.register(SearchHistory)
admin.site.register(RecommendationCache)
