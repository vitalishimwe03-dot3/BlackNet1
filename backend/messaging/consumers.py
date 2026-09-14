from datetime import timedelta

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from asgiref.sync import sync_to_async
from django.utils import timezone

from messaging.models import Conversation, ConversationMember, Message
from messaging.serializers import MessageSerializer


class ConversationConsumer(AsyncJsonWebsocketConsumer):
    """WebSocket client for real-time messaging within a conversation.

    Authentication happens via the JWT passed as ``?token=`` query param;
    Django Channels' AuthMiddlewareStack handles session auth first, and this
    consumer additionally verifies JWT credentials and conversation membership.
    """

    async def connect(self):
        user = await self._authenticate()
        if user is None:
            await self.close(code=4003)
            return
        self.user = user
        self.conversation_id = self.scope["url_route"]["kwargs"]["conversation_id"]
        self.group_name = f"conversation_{self.conversation_id}"

        allowed = await self._is_member(user, self.conversation_id)
        if not allowed:
            await self.close(code=4003)
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self.send_json({"event": "connected", "payload": {"detail": "CHANNEL LINKED"}})

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        event = content.get("event", "message.send")

        if event == "message.send":
            msg = await self._create_message(self.user, content.get("content", ""))
            if msg:
                await self.channel_layer.group_send(
                    self.group_name,
                    {"type": "conversation.event", "event": "message.new", "payload": msg},
                )
        elif event == "typing":
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "typing.event",
                    "payload": {"user": self.user.username, "typing": bool(content.get("typing"))},
                },
            )
        elif event == "mark_read":
            await self._mark_read(self.user)

    # ---------- channel group receivers ---------- #
    async def conversation_event(self, event):
        await self.send_json({"event": event["event"], "payload": event["payload"]})

    async def typing_event(self, event):
        await self.send_json({"event": "typing", "payload": event["payload"]})

    # ---------- sync-to-async helpers ---------- #
    @sync_to_async
    def _authenticate(self):
        from rest_framework_simplejwt.authentication import JWTAuthentication
        from rest_framework_simplejwt.exceptions import InvalidToken

        token = self.scope["query_string"].decode()
        token_value = ""
        for part in token.split("&"):
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

    @sync_to_async
    def _is_member(self, user, conversation_id):
        return ConversationMember.objects.filter(
            conversation_id=conversation_id, user=user
        ).exists()

    @sync_to_async
    def _create_message(self, user, content):
        if not content.strip():
            return None
        conv = Conversation.objects.filter(pk=self.conversation_id).first()
        if not conv:
            return None
        msg = Message.objects.create(sender=user, conversation=conv, content=content.strip())
        conv.last_message = msg.content[:400]
        conv.last_message_at = timezone.now()
        conv.save(update_fields=["last_message", "last_message_at"])
        ConversationMember.objects.filter(conversation=conv, user=user).update(
            last_read_at=timezone.now(), is_typing=False
        )
        return MessageSerializer(msg).data

    @sync_to_async
    def _mark_read(self, user):
        ConversationMember.objects.filter(
            conversation_id=self.conversation_id, user=user
        ).update(last_read_at=timezone.now())