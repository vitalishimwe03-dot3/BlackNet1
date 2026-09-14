from rest_framework import viewsets
from rest_framework.response import Response

from .models import Notification
from .serializers import NotificationSerializer


class NotificationViewSet(viewsets.ModelViewSet):
    """GET /api/notifications, POST /api/notifications/{id}/read, etc."""

    serializer_class = NotificationSerializer

    def get_queryset(self):
        qs = Notification.objects.filter(recipient=self.request.user)
        unread = self.request.query_params.get("unread")
        if unread == "true":
            qs = qs.filter(is_read=False)
        return qs

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_read = True
        instance.save(update_fields=["is_read"])
        return self.retrieve(request, *args, **kwargs)

    def perform_destroy(self, instance):
        instance.delete()


class MarkAllReadView(viewsets.ViewSet):
    def create(self, request):
        Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
        return Response({"detail": "ALL_READ"})