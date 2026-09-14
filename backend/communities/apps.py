from django.apps import AppConfig
from django.db.models.signals import post_save
from django.dispatch import receiver


class CommunitiesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "communities"


@receiver(post_save, sender="communities.Community")
def seed_default_channels(sender, instance, created, **kwargs):
    if created:
        from .models import CommunityChannel

        CommunityChannel.objects.get_or_create(community=instance, name="general", description="General discussion")