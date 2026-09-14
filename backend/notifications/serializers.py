from rest_framework import serializers

from posts.serializers import PostSerializer
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    post_detail = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            "id", "actor", "kind", "message",
            "post", "message_obj", "file", "data",
            "is_read", "created_at", "post_detail",
        ]
        read_only_fields = fields

    def get_post_detail(self, obj):
        if obj.post:
            from posts.serializers import PostSerializer
            return {
                "post_id": str(obj.post.pk),
                "content": obj.post.content[:200] if obj.post.content else obj.post.post_type,
            }
        return None