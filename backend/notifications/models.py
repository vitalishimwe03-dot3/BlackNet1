import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="sent_notifications"
    )
    kind = models.CharField(max_length=32, db_index=True, default="system")
    message = models.CharField(max_length=255)
    post = models.ForeignKey("posts.Post", on_delete=models.CASCADE, null=True, blank=True)
    message_obj = models.ForeignKey("messaging.Message", on_delete=models.CASCADE, null=True, blank=True)
    file = models.ForeignKey("files.File", on_delete=models.CASCADE, null=True, blank=True)
    data = models.JSONField(default=dict, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["recipient", "is_read", "-created_at"])]

    def __str__(self):
        return f"{self.recipient}: {self.message}"