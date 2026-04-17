from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError


class User(AbstractUser):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)

    ROLE_CHOICES = (
        ('user', 'User'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def save(self, *args, **kwargs):
        if self.pk:
            old = User.objects.get(pk=self.pk)
            if old.role != self.role:
                if not kwargs.pop('allow_role_change', False):
                    raise ValidationError(
                        "You are not allowed to change the account role this way."
                    )
        super().save(*args, **kwargs)


class Movie(models.Model):
    tmdb_id = models.IntegerField(unique=True)
    title = models.CharField(max_length=255)
    poster_path = models.CharField(max_length=255, blank=True, null=True)
    release_date = models.DateField(blank=True, null=True)
    cached_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'movie')


class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchlist')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'movie')


class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    rating = models.FloatField()
    rated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'movie')


class SearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='searches')
    query = models.CharField(max_length=255)
    searched_at = models.DateTimeField(auto_now_add=True)


class RecommendationCache(models.Model):
    CACHE_TYPE_CHOICES = (
        ('search_history', 'Search History'),
        ('ratings', 'Ratings'),
        ('hybrid', 'Hybrid'),
    )

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='recommendation_caches'
    )
    cache_type = models.CharField(max_length=20, choices=CACHE_TYPE_CHOICES)
    data = models.JSONField()
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'cache_type')
