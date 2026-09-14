from django.utils import timezone
from rest_framework import viewsets, mixins, generics, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle

from users.authentication_helpers import request_ip
from .models import Report, AuditLog
from .serializers import ReportSerializer, ReportModerateSerializer, AuditLogSerializer


class ReportViewSet(viewsets.ModelViewSet[mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin]):
    """POST /api/moderation/reports — anyone can file a report."""

    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "user"

    def get_queryset(self):
        # Users only see their own reports; admins see all via the moderation queue.
        if self.request.user.is_staff:
            return Report.objects.all()
        return Report.objects.filter(reporter=self.request.user)

    def perform_create(self, serializer):
        report = serializer.save(reporter=self.request.user)
        AuditLog.objects.create(
            user=self.request.user,
            action="REPORT_CREATED",
            target_type=report.target_type,
            target_id=report.target_id,
            ip_address=request_ip(self.request),
        )


class ModerationQueueView(generics.ListAPIView):
    """GET /api/moderation/queue — staff only."""

    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        qs = Report.objects.exclude(status="dismissed")
        status_filter = self.request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter)
        category = self.request.query_params.get("category")
        if category:
            qs = qs.filter(category=category)
        return qs

    def get(self, request, *args, **kwargs):
        if request.query_params.get("stats") == "true":
            from django.db.models import Count

            stats = Report.objects.values("status", "category").annotate(count=Count("id"))
            return Response(list(stats))
        return super().get(request, *args, **kwargs)


class ModerationResolveView(generics.GenericAPIView):
    """POST /api/moderation/reports/{id}/resolve — staff only."""

    permission_classes = [permissions.IsAdminUser]
    serializer_class = ReportModerateSerializer

    def post(self, request, pk):
        report = Report.objects.filter(pk=pk).first()
        if not report:
            return Response({"detail": "NOT_FOUND"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        report.status = serializer.validated_data["status"]
        report.resolution_note = serializer.validated_data.get("resolution_note", "")
        report.resolved_by = request.user
        report.resolved_at = timezone.now()
        report.save()

        AuditLog.objects.create(
            user=request.user,
            action="REPORT_RESOLVED",
            target_type=report.target_type,
            target_id=report.target_id,
            ip_address=request_ip(request),
        )
        return Response(ReportSerializer(report).data)


class AuditLogViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """GET /api/moderation/audit — staff only."""

    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        qs = AuditLog.objects.all()
        action = self.request.query_params.get("action")
        if action:
            qs = qs.filter(action=action)
        return qs