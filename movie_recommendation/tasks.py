from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import User, Movie, Rating

@shared_task
def registration_confirmation_email(user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return f"User with id {user_id} does not exist"

    subject = f'Welcome to Movie Recommendation!'
    message = (
        f'Dear {user.username},\n\n'
        f'Thank you for registering with Movie Recommendation!\n\n'
        f'Best regards,\n'
        f'The Movie Recommendation Team'
    )

    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL,
               [user.email], fail_silently=False)

    print(f"Sent registration confirmation email to {user.email}")
