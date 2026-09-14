from django.urls import path
from rest_framework.routers import SimpleRouter

from notifications.views import NotificationViewSet, MarkAllReadView

router = SimpleRouter()
router.register("", NotificationViewSet, basename="notifications")

urlpatterns = router.urls + [
    path("read-all", MarkAllReadView.as_view({"post": "create"}), name="notifications_read_all"),
]