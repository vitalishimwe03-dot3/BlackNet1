from django.urls import path
from rest_framework.routers import SimpleRouter

from moderation.views import ReportViewSet, ModerationQueueView, ModerationResolveView, AuditLogViewSet

router = SimpleRouter()
router.register("reports", ReportViewSet, basename="reports")
router.register("audit", AuditLogViewSet, basename="audit")

urlpatterns = router.urls + [
    path("queue", ModerationQueueView.as_view(), name="moderation_queue"),
    path("reports/<uuid:pk>/resolve", ModerationResolveView.as_view(), name="moderation_resolve"),
]