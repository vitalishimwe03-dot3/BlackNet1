"""User signals: guaranteed profile creation."""
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def ensure_profile(sender, instance, created, **kwargs):
    from .models import UserProfile

    if created:
        UserProfile.objects.get_or_create(user=instance)