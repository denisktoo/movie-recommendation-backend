import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "movie_recommendation_backend.settings")

app = Celery("movie_recommendation_backend")

# Read config from Django settings, using CELERY_ prefix for all celery-related settings
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks.py in installed apps
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
