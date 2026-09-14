from rest_framework import serializers

from users.serializers import UserSerializer
from .models import Post, Comment, Like, Bookmark, PollVote


class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    like_count = serializers.IntegerField(read_only=True)
    comment_count = serializers.IntegerField(read_only=True)
    liked_by_me = serializers.SerializerMethodField()
    bookmarked_by_me = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id", "author", "content", "post_type", "community",
            "image", "video", "file", "link_url", "poll_data",
            "view_count", "is_edited", "created_at", "updated_at",
            "like_count", "comment_count", "liked_by_me", "bookmarked_by_me",
        ]
        read_only_fields = ["id", "view_count", "created_at", "updated_at", "like_count", "comment_count"]

    def get_liked_by_me(self, obj):
        user = self.context.get("request").user if self.context.get("request") else None
        if not user or not user.is_authenticated:
            return False
        return Like.objects.filter(post=obj, user=user).exists()

    def get_bookmarked_by_me(self, obj):
        user = self.context.get("request").user if self.context.get("request") else None
        if not user or not user.is_authenticated:
            return False
        return Bookmark.objects.filter(post=obj, user=user).exists()


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    like_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "post", "author", "parent", "content", "is_deleted", "created_at", "like_count"]
        read_only_fields = ["id", "author", "created_at"]


class PollVoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = PollVote
        fields = ["poll", "choice"]
        read_only_fields = ["user"]

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)