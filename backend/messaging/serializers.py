from rest_framework import serializers

from users.serializers import UserSerializer
from .models import Conversation, ConversationMember, Message


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    reply_preview = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            "id", "conversation", "sender", "content", "reply_to",
            "attachment_file", "attachment_image", "attachment_video",
            "read_by", "reactions", "is_edited", "is_deleted", "created_at",
            "reply_preview",
        ]
        read_only_fields = ["id", "sender", "created_at"]

    def get_reply_preview(self, obj):
        if obj.reply_to:
            return obj.reply_to.content[:120]
        return None


class ConversationSerializer(serializers.ModelSerializer):
    members = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            "id", "type", "name", "created_at", "last_message_at",
            "last_message", "members", "unread_count", "partner",
        ]

    def get_members(self, obj):
        from users.serializers import UserSerializer
        members = [m.user for m in obj.members.select_related("user")]
        return UserSerializer(members, many=True).data

    def get_unread_count(self, obj):
        user = self.context.get("request").user if self.context.get("request") else None
        if not user:
            return 0
        member = obj.members.filter(user=user).first()
        if not member:
            return 0
        return Message.objects.filter(
            conversation=obj, created_at__gt=member.last_read_at, is_deleted=False
        ).exclude(sender=user).count()


class ConversationMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConversationMember
        fields = ["id", "conversation", "user", "joined_at", "last_read_at", "is_typing"]