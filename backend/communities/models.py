import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class Community(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=64, unique=True)
    slug = models.SlugField(max_length=80, unique=True)
    description = models.TextField(max_length=2000, blank=True, default="")
    icon = models.ImageField(upload_to="communities/icons/", null=True, blank=True)
    banner = models.ImageField(upload_to="communities/banners/", null=True, blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="owned_communities")
    visibility = models.CharField(max_length=16, choices=[("public", "Public"), ("private", "Private")], default="public")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["name"]), models.Index(fields=["slug"])]

    def __str__(self):
        return self.name


class CommunityMember(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name="members")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="community_memberships")
    role = models.CharField(
        max_length=16,
        choices=[("member", "Member"), ("moderator", "Moderator"), ("owner", "Owner")],
        default="member",
    )
    is_banned = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["community", "user"], name="uniq_community_member")]
        indexes = [models.Index(fields=["community", "role"])]

    def __str__(self):
        return f"{self.user} in {self.community}"


class CommunityChannel(models.Model):
    """Discussion channels inside a community (e.g. general, linux, ai)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name="channels")
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=500, blank=True, default="")

    class Meta:
        unique_together = [["community", "name"]]

    def __str__(self):
        return f"{self.community.name}/{self.name}"