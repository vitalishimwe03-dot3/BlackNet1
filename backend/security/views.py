from django.utils import timezone
from rest_framework import generics, viewsets
from rest_framework.response import Response

from users.models import UserSession
from users.serializers import SessionSerializer
from .models import SecurityEvent
from .serializers import SecurityEventSerializer


class SecurityOverviewView(generics.GenericAPIView):
    """GET /api/security/overview — SECURITY://CENTER snapshot."""

    serializer_class = SecurityEventSerializer

    def get(self, request):
        user = request.user
        sessions = UserSession.objects.filter(user=user, revoked_at__isnull=True).order_by("-last_seen")
        login_history = SecurityEvent.objects.filter(user=user, event_type__in=["LOGIN_SUCCESS", "LOGIN_FAILED"])
        password_changes = SecurityEvent.objects.filter(user=user, event_type="PASSWORD_CHANGED").count()
        suspicious = SecurityEvent.objects.filter(user=user, event_type="SUSPICIOUS_LOGIN").count()
        devices = sessions.distinct()

        return Response({
            "sessions": SessionSerializer(sessions, many=True).data,
            "login_history": SecurityEventSerializer(login_history, many=True).data,
            "password_changes": password_changes,
            "two_factor_enabled": user.is_2fa_enabled,
            "suspicious_logins": suspicious,
            "device_count": devices.count(),
        })


class SecurityEventViewSet(viewsets.GenericViewSet):
    """GET /api/security/events."""

    serializer_class = SecurityEventSerializer

    def get_queryset(self):
        return SecurityEvent.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        event_type = request.query_params.get("type")
        if event_type:
            qs = qs.filter(event_type=event_type)
        page = self.paginate_queryset(qs)
        return self.get_paginated_response(SecurityEventSerializer(page, many=True).data)


class ActiveSessionListView(generics.ListAPIView):
    """GET /api/security/sessions — active sessions for security center."""

    serializer_class = SessionSerializer

    def get_queryset(self):
        return UserSession.objects.filter(user=self.request.user, revoked_at__isnull=True).order_by("-last_seen")