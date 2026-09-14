from channels.generic.websocket import AsyncJsonWebsocketConsumer
from asgiref.sync import sync_to_async


class NotificationConsumer(AsyncJsonWebsocketConsumer):
    """Live notification stream. Auth via ?token=<jwt> or channels session user."""

    async def connect(self):
        user = await self._authenticate()
        if user is None:
            await self.close(code=4003)
            return
        self.user = user
        self.group_name = f"notifications_{user.pk}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self.send_json({"event": "connected", "payload": {"detail": "NOTIFICATION_LINK"}})

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def notification_event(self, event):
        await self.send_json({"event": "notification", "payload": event["payload"]})

    async def receive_json(self, content, **kwargs):
        # No client->server commands needed for notifications; ack heartbeat.
        if content.get("event") == "ping":
            await self.send_json({"event": "pong"})

    @sync_to_async
    def _authenticate(self):
        from rest_framework_simplejwt.authentication import JWTAuthentication
        from rest_framework_simplejwt.exceptions import InvalidToken

        qs = self.scope["query_string"].decode()
        token_value = ""
        for part in qs.split("&"):
            if part.startswith("token="):
                token_value = part.split("=", 1)[1]
        if not token_value and self.scope.get("user") and getattr(self.scope["user"], "is_authenticated", False):
            return self.scope["user"]
        if not token_value:
            return None
        try:
            validator = JWTAuthentication()
            validated = validator.get_validated_token(token_value)
            return validator.get_user(validated)
        except InvalidToken:
            return None