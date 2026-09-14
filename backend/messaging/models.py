import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class Conversation(models.Model):
    """A private (DM) or group conversation."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=16, choices=[("private", "private"), ("group", "group")], default="private")
    name = models.CharField(max_length=128, blank=True, default="")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="created_conversations")
    created_at = models.DateTimeField(auto_now_add=True)
    last_message_at = models.DateTimeField(default=timezone.now, db_index=True)

    # Denormalized last message preview for list views
    last_message = models.TextField(max_length=400, blank=True, default="")

    # For private DMs: the direct partner (authored by DM sender)
    partner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="direct_conversations"
    )

    class Meta:
        indexes = [models.Index(fields=["last_message_at"])]

    def __str__(self):
        return self.name or self.type


class ConversationMember(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="members")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="conversations")
    joined_at = models.DateTimeField(auto_now_add=True)
    last_read_at = models.DateTimeField(default=timezone.now)
    is_typing = models.BooleanField(default=False)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["conversation", "user"], name="uniq_conversation_member")]
        indexes = [models.Index(fields=["user", "last_read_at"])]

    def __str__(self):
        return f"{self.user} in {self.conversation}"


class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="messages")
    content = models.TextField(max_length=10000, blank=True, default="")
    reply_to = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="replies")
    # Attachments
    attachment_file = models.ForeignKey("files.File", on_delete=models.SET_NULL, null=True, blank=True)
    attachment_image = models.ImageField(upload_to="messages/images/", null=True, blank=True)
    attachment_video = models.FileField(upload_to="messages/videos/", null=True, blank=True)

    read_by = models.JSONField(default=list, blank=True)
    reactions = models.JSONField(default=dict, blank=True)
    is_edited = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        ordering = ["created_at"]
        indexes = [models.Index(fields=["conversation", "created_at"])]

    def __str__(self):
        return f"{self.sender_id}: {self.content[:40]}"


class Presence(models.Model):
    """Lightweight user-presence store used by the WebSocket layer + UI."""

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="presence")
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(default=timezone.now)
    current_room = models.CharField(max_length=128, blank=True, default="")

    def __str__(self):
        return f"{self.user} {'ONLINE' if self.is_online else 'OFFLINE'}"