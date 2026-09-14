from django.urls import path
from rest_framework.routers import SimpleRouter

from security.views import SecurityOverviewView, SecurityEventViewSet, ActiveSessionListView

router = SimpleRouter()
router.register("events", SecurityEventViewSet, basename="security_events")

urlpatterns = router.urls + [
    path("overview", SecurityOverviewView.as_view(), name="security_overview"),
    path("sessions", ActiveSessionListView.as_view(), name="security_sessions"),
]