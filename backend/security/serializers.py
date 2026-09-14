from rest_framework import serializers

from users.models import UserSession
from .models import SecurityEvent


class SecurityEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecurityEvent
        fields = ["id", "event_type", "ip_address", "user_agent", "details", "created_at"]
        read_only_fields = fields


class SecurityOverviewSerializer(serializers.Serializer):
    """Computed security center snapshot."""

    sessions = serializers.ListField()
    login_history = serializers.ListField()
    password_changes = serializers.IntegerField()
    two_factor_enabled = serializers.BooleanField()
    suspicious_logins = serializers.IntegerField()
    device_count = serializers.IntegerField()


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSession
        fields = ["id", "user_agent", "device_name", "ip_address", "is_current", "last_seen"]