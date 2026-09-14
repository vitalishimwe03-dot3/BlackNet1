import json

from django.utils import timezone
from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.throttling import ScopedRateThrottle
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from notifications.services import notify
from security.models import SecurityEvent
from .models import Conversation, ConversationMember, Message
from .serializers import ConversationSerializer, MessageSerializer


def ws_conversation_group(cid):
    return f"conversation_{cid}"


def push_message_event(conversation, event_type, payload):
    layer = get_channel_layer()
    async_to_sync(layer.group_send)(
        ws_conversation_group(conversation.pk),
        {"type": "conversation.event", "event": event_type, "payload": payload},
    )


class ConversationViewSet(viewsets.ModelViewSet):
    """DM / group conversations."""

    serializer_class = ConversationSerializer

    def get_queryset(self):
        return Conversation.objects.filter(members__user=self.request.user).order_by("-last_message_at").distinct()

    def perform_create(self, serializer):
        conv = serializer.save(created_by=self.request.user)
        ConversationMember.objects.create(conversation=conv, user=self.request.user)

    @action(detail=False, methods=["post"])
    def direct(self, request):
        """POST /api/messages/direct { username } -> create/find DM."""
        from django.contrib.auth import get_user_model

        username = request.data.get("username")
        user = get_user_model().objects.filter(username=username, is_active=True).first()
        if not user or user == request.user:
            return Response({"detail": "INVALID_USER"}, status=status.HTTP_400_BAD_REQUEST)

        # find existing DM between users
        my_convos = Conversation.objects.filter(type="private", members__user=request.user)
        for conv in my_convos:
            if conv.members.filter(user=user).exists():
                return Response({"id": conv.pk, "type": "private", "partner": user.username})
        conv = Conversation.objects.create(type="private", partner=user)
        ConversationMember.objects.create(conversation=conv, user=request.user)
        ConversationMember.objects.create(conversation=conv, user=user)
        return Response({"id": conv.pk, "type": "private", "partner": user.username})

    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        conv = self.get_object()
        member = conv.members.filter(user=request.user).first()
        if member:
            member.last_read_at = timezone.now()
            member.save(update_fields=["last_read_at"])
        return Response({"detail": "READ"})

    @action(detail=True, methods=["get"])
    def history(self, request, pk=None):
        conv = self.get_object()
        msgs = Message.objects.filter(conversation=conv, is_deleted=False).select_related("sender").order_by("-created_at")
        page = self.paginate_queryset(msgs)
        data = MessageSerializer(page, many=True, context={"request": request}).data
        return self.get_paginated_response(data[::-1])

    @action(detail=True, methods=["get"])
    def search(self, request, pk=None):
        conv = self.get_object()
        q = request.query_params.get("q", "")
        msgs = Message.objects.filter(conversation=conv, is_deleted=False, content__icontains=q)
        page = self.paginate_queryset(msgs)
        return self.get_paginated_response(MessageSerializer(page, many=True, context={"request": request}).data)

    @action(detail=False, methods=["post"])
    def ensure_group(self, request):
        """POST /api/messages/group { name, members: [usernames] }"""
        name = request.data.get("name", "")
        usernames = request.data.get("members", [])
        from django.contrib.auth import get_user_model

        members = list(get_user_model().objects.filter(username__in=usernames, is_active=True))
        members.append(request.user)
        if len(members) < 1:
            return Response({"detail": "NO_MEMBERS"}, status=status.HTTP_400_BAD_REQUEST)
        conv = Conversation.objects.create(type="group", name=name, created_by=request.user)
        for m in members:
            ConversationMember.objects.create(conversation=conv, user=m)
        return Response(ConversationSerializer(conv, context={"request": request}).data)


class MessageSendView(generics.CreateAPIView):
    """POST /api/messages/{conversation_id}/send"""

    serializer_class = MessageSerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "messages"

    def create(self, request, pk=None):
        conv = Conversation.objects.filter(pk=pk, members__user=request.user).first()
        if not conv:
            return Response({"detail": "NOT_FOUND"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = serializer.save(sender=request.user, conversation=conv)
        conv.last_message = message.content[:400]
        conv.last_message_at = timezone.now()
        conv.save(update_fields=["last_message", "last_message_at"])
        # reset typing
        ConversationMember.objects.filter(conversation=conv, user=request.user).update(is_typing=False)

        payload = MessageSerializer(message, context={"request": request}).data
        push_message_event(conv, "message.new", payload)

        # Notify all other members
        for member in conv.members.exclude(user=request.user):
            if member.user.notify_new_messages:
                notify(member.user, f"NEW MESSAGE FROM @{request.user.username}", kind="message", message=message)

        SecurityEvent.objects.create(user=request.user, event_type="MESSAGE_SENT")
        return Response(payload, status=status.HTTP_201_CREATED)


class MessageActionView(generics.GenericAPIView):
    """POST /api/messages/{id}/edit|react|read|delete"""

    def post(self, request, pk):
        msg = Message.objects.filter(pk=pk, sender=request.user).first()
        if not msg:
            return Response({"detail": "NOT_FOUND"}, status=status.HTTP_404_NOT_FOUND)

        action = request.query_params.get("action") or request.data.get("action")
        if action == "edit":
            msg.content = request.data.get("content", msg.content)
            msg.is_edited = True
            msg.save(update_fields=["content", "is_edited"])
        elif action == "delete":
            msg.is_deleted = True
            msg.save(update_fields=["is_deleted"])
        elif action == "react":
            emoji = request.data.get("emoji")
            if not emoji:
                return Response({"detail": "EMOJI_REQUIRED"}, status=status.HTTP_400_BAD_REQUEST)
            reactions = dict(msg.reactions or {})
            uid = str(request.user.pk)
            if uid in reactions and reactions[uid] == emoji:
                del reactions[uid]
            else:
                reactions[uid] = emoji
            msg.reactions = reactions
            msg.save(update_fields=["reactions"])

        payload = MessageSerializer(msg, context={"request": request}).data
        push_message_event(msg.conversation, "message.update", payload)
        return Response(payload)

    def get(self, request, pk):
        """Mark a message read by current user."""
        msg = Message.objects.filter(pk=pk).first()
        if msg and request.user.pk not in msg.read_by:
            read = list(msg.read_by) + [str(request.user.pk)]
            msg.read_by = read
            msg.save(update_fields=["read_by"])
        return Response({"detail": "READ"})