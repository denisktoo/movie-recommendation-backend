from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, RecommendationCache

@receiver(post_save, sender=User)
def create_recommendation_cache(sender, instance, created, **kwargs):
    if created:
        RecommendationCache.objects.create(user=instance, data={})
