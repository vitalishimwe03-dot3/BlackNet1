"""Django signals keeping storage accounting in sync with file deletions."""
from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import File
from .services import recalculate_storage


@receiver(post_delete, sender=File)
def file_deleted(sender, instance, **kwargs):
    recalculate_storage(instance.owner)