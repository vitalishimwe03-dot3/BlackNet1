from rest_framework import serializers

from users.serializers import UserSerializer
from .models import Community, CommunityMember, CommunityChannel


class CommunitySerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()
    joined_by_me = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    owner = UserSerializer(read_only=True)

    class Meta:
        model = Community
        fields = [
            "id", "name", "slug", "description", "icon", "banner",
            "owner", "visibility", "is_active", "created_at",
            "member_count", "joined_by_me", "role",
        ]
        read_only_fields = ["id", "slug", "owner", "is_active", "created_at", "member_count"]

    def get_member_count(self, obj):
        return obj.members.count()

    def get_joined_by_me(self, obj):
        user = self.context.get("request").user if self.context.get("request") else None
        if user and user.is_authenticated:
            return obj.members.filter(user=user).exists()
        return False

    def get_role(self, obj):
        user = self.context.get("request").user if self.context.get("request") else None
        if user and user.is_authenticated:
            member = obj.members.filter(user=user).first()
            return member.role if member else None
        return None


class CommunityCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Community
        fields = ["name", "slug", "description", "icon", "banner", "visibility"]
        read_only_fields = []

    def validate_slug(self, value):
        value = value.lower()
        return value


class CommunityMemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = CommunityMember
        fields = ["id", "user", "role", "joined_at"]
        read_only_fields = ["id", "joined_at"]


class CommunityChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunityChannel
        fields = ["id", "community", "name", "description"]
        read_only_fields = ["id"]