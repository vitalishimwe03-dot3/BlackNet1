from rest_framework import serializers

from .models import Report, AuditLog


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = [
            "id", "reporter", "category", "target_type", "target_id",
            "reason", "status", "resolution_note", "created_at", "resolved_at",
        ]
        read_only_fields = ["id", "reporter", "status", "resolution_note", "created_at", "resolved_at"]


class ReportModerateSerializer(serializers.Serializer):
    """Admin resolution of a report."""

    status = serializers.ChoiceField(choices=["resolved", "dismissed"])
    resolution_note = serializers.CharField(required=False, allow_blank=True, max_length=2000)


class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = ["id", "user", "action", "target_type", "target_id", "details", "ip_address", "created_at"]
        read_only_fields = fields