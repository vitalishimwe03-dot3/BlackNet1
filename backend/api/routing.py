"""WebSocket routing for the realtime layer (messaging + notifications)."""
from django.urls import re_path

from messaging.consumers import ConversationConsumer
from notifications.consumers import NotificationConsumer

websocket_urlpatterns = [
    re_path(r"^ws/conversations/(?P<conversation_id>[0-9a-f-]+)/?$", ConversationConsumer.as_asgi()),
    re_path(r"^ws/notifications/?$", NotificationConsumer.as_asgi()),
]