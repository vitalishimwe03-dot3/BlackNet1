import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """Extended user with platform-specific fields."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=32, unique=True)
    email = models.EmailField(unique=True)
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True, default="")
    is_email_verified = models.BooleanField(default=False)
    last_active = models.DateTimeField(default=timezone.now)
    is_online = models.BooleanField(default=False)
    is_2fa_enabled = models.BooleanField(default=False)
    two_factor_secret = models.CharField(max_length=64, blank=True, default="")
    reputation_public = models.BooleanField(default=True)
    storage_bytes_total = models.BigIntegerField(default=settings.DEFAULT_USER_STORAGE_BYTES)
    storage_bytes_used = models.BigIntegerField(default=0)

    # Privacy settings
    profile_visibility = models.CharField(
        max_length=16,
        choices=[("public", "Public"), ("private", "Private"), ("followers", "Followers only")],
        default="public",
    )

    # Notification settings
    notify_new_messages = models.BooleanField(default=True)
    notify_likes = models.BooleanField(default=True)
    notify_comments = models.BooleanField(default=True)
    notify_followers = models.BooleanField(default=True)
    notify_mentions = models.BooleanField(default=True)
    notify_community = models.BooleanField(default=True)
    notify_security = models.BooleanField(default=True)
    email_notifications = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["username"]),
            models.Index(fields=["email"]),
            models.Index(fields=["last_active"]),
        ]

    def __str__(self):
        return self.username

    @property
    def storage_used_display(self):
        return self.storage_bytes_used / (1024**3)

    @property
    def storage_total_display(self):
        return self.storage_bytes_total / (1024**3)


class UserProfile(models.Model):
    """Public profile details."""

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    display_name = models.CharField(max_length=64, blank=True, default="")
    location = models.CharField(max_length=128, blank=True, default="")
    website = models.URLField(blank=True, default="")
    github = models.CharField(max_length=64, blank=True, default="")
    bio = models.TextField(max_length=500, blank=True, default="")
    reputation = models.IntegerField(default=0)
    badges = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class UserSession(models.Model):
    """Active user sessions/devices tracked for the security center."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sessions")
    token_id = models.CharField(max_length=64, db_index=True)
    user_agent = models.CharField(max_length=512, blank=True, default="")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    device_name = models.CharField(max_length=128, blank=True, default="")
    is_current = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)
    revoked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["token_id"]),
        ]

    def __str__(self):
        return f"{self.user.username} @ {self.device_name or self.ip_address}"