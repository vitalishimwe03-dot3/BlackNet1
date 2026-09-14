import uuid

from django.conf import settings
from django.db import models


class SecurityEvent(models.Model):
    """Auditable security events surfaced in the Security Center."""

    EVENT_TYPES = [
        ("LOGIN_SUCCESS", "Login success"),
        ("LOGIN_FAILED", "Login failed"),
        ("LOGOUT", "Logout"),
        ("PASSWORD_CHANGED", "Password changed"),
        ("2FA_ENABLED", "2FA enabled"),
        ("2FA_DISABLED", "2FA disabled"),
        ("SESSION_REVOKED", "Session revoked"),
        ("SUSPICIOUS_LOGIN", "Suspicious login"),
        ("FILE_UPLOADED", "File uploaded"),
        ("ACCOUNT_REGISTERED", "Account registered"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="security_events")
    event_type = models.CharField(max_length=32, choices=EVENT_TYPES, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=512, blank=True, default="")
    details = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user", "-created_at"]), models.Index(fields=["event_type"])]

    def __str__(self):
        return f"{self.user}: {self.event_type}"