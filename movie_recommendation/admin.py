from django.contrib import admin

from .models import (
    Favorite,
    Movie,
    Rating,
    RecommendationCache,
    SearchHistory,
    User,
    Watchlist,
)

admin.site.register(User)
admin.site.register(Movie)
admin.site.register(Favorite)
admin.site.register(Watchlist)
admin.site.register(Rating)
admin.site.register(SearchHistory)
admin.site.register(RecommendationCache)
