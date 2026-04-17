import django_filters
from .models import (
    Movie, Favorite
)


class MovieFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(field_name='title', lookup_expr='icontains')
    release = django_filters.DateFilter(field_name='release_date', lookup_expr='exact')
    release_date_after = django_filters.DateFilter(
        field_name='release_date', lookup_expr='gte'
    )
    release_date_before = django_filters.DateFilter(
        field_name='release_date', lookup_expr='lte'
    )

    class Meta:
        model = Movie
        fields = ['title', 'release', 'release_date_after', 'release_date_before']


class FavoriteFilter(django_filters.FilterSet):
    user_id = django_filters.NumberFilter(field_name='user__id')
    movie_id = django_filters.NumberFilter(field_name='movie__id')

    class Meta:
        model = Favorite
        fields = ['user_id', 'movie_id']
