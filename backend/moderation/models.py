import uuid

from django.conf import settings
from django.db import models


class Report(models.Model):
    CATEGORY_CHOICES = [
        ("spam", "Spam"),
        ("harassment", "Harassment"),
        ("illegal", "Illegal content"),
        ("malicious", "Malicious content"),
        ("copyright", "Copyright"),
        ("other", "Other"),
    ]
    TARGET_TYPES = [
        ("post", "Post"),
        ("message", "Message"),
        ("profile", "Profile"),
        ("community", "Community"),
        ("file", "File"),
    ]
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("reviewing", "Reviewing"),
        ("resolved", "Resolved"),
        ("dismissed", "Dismissed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reports")
    category = models.CharField(max_length=16, choices=CATEGORY_CHOICES)
    target_type = models.CharField(max_length=16, choices=TARGET_TYPES)
    target_id = models.CharField(max_length=64)
    reason = models.TextField(max_length=2000, blank=True, default="")
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="pending")
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="resolved_reports"
    )
    resolution_note = models.TextField(max_length=2000, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["status", "-created_at"]), models.Index(fields=["target_type", "target_id"])]

    def __str__(self):
        return f"{self.reporter} -> {self.target_type}:{self.target_id} ({self.category})"


class AuditLog(models.Model):
    """Immutable audit trail for admin actions and security events."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="audit_logs")
    action = models.CharField(max_length=64, db_index=True)
    target_type = models.CharField(max_length=32, blank=True, default="")
    target_id = models.CharField(max_length=64, blank=True, default="")
    details = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user", "-created_at"]), models.Index(fields=["-created_at"])]

    def __str__(self):
        return f"{self.user or 'SYSTEM'}: {self.action}"