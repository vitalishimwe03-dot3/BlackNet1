from django.urls import path
from rest_framework.routers import SimpleRouter

from messaging.views import ConversationViewSet, MessageSendView, MessageActionView

router = SimpleRouter()
router.register("", ConversationViewSet, basename="conversations")

urlpatterns = router.urls + [
    path("<uuid:conversation_id>/send", MessageSendView.as_view(), name="message_send"),
    path("<uuid:pk>/edit", MessageActionView.as_view(), name="message_edit"),
]