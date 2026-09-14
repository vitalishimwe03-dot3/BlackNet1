from django.db.models import Count, Exists, OuterRef
from rest_framework import generics, viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle

from notifications.services import notify, notify_mention
from security.models import SecurityEvent
from .models import Post, Comment, Like, Follow, Bookmark, PollVote
from .serializers import PostSerializer, CommentSerializer, PollVoteSerializer


def annotate_post_queryset(qs, user):
    return qs.annotate(
        like_count=Count("likes", distinct=True),
        comment_count=Count("comments", distinct=True),
    )


class PostViewSet(viewsets.ModelViewSet):
    """Feed posts. GET /api/posts, POST /api/posts/{id}/like, etc."""

    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_scope = "user"

    def get_queryset(self):
        # Coming soon: also pull posts from followed users. Keep to author+communities now to stay fast.
        qs = Post.objects.filter(is_deleted=False).select_related("author").order_by("-created_at")
        qs = annotate_post_queryset(qs, self.request.user)
        community = self.request.query_params.get("community")
        if community:
            qs = qs.filter(community_id=community)
        return qs

    def perform_create(self, serializer):
        post = serializer.save(author=self.request.user)
        SecurityEvent.objects.create(user=self.request.user, event_type="POST_CREATED")

    @action(detail=True, methods=["post"])
    def like(self, request, pk=None):
        post = self.get_object()
        like, created = Like.objects.get_or_create(user=request.user, post=post)
        if not created:
            like.delete()
        if created and post.author != request.user and post.author.notify_likes:
            notify(post.author, f"NEW LIKE ON YOUR TRANSMISSION", post=post, kind="like")
        return Response({"liked": created, "like_count": like_count_for(post)})

    @action(detail=True, methods=["post"], throttle_scope="user")
    def bookmark(self, request, pk=None):
        post = self.get_object()
        bm, created = Bookmark.objects.get_or_create(user=request.user, post=post)
        if not created:
            bm.delete()
        return Response({"bookmarked": created})

    @action(detail=True, methods=["post"])
    def increment_view(self, request, pk=None):
        post = self.get_object()
        Post.objects.filter(pk=post.pk).update(view_count=post.view_count + 1)
        return Response({"view_count": post.view_count + 1})

    @action(detail=True, methods=["get"])
    def comments(self, request, pk=None):
        post = self.get_object()
        comments = Comment.objects.filter(post=post, is_deleted=False).annotate(
            like_count=Count("likes")
        ).select_related("author").order_by("created_at")
        page = self.paginate_queryset(comments)
        return self.get_paginated_response(CommentSerializer(page, many=True, context={"request": request}).data)


def like_count_for(post):
    return Like.objects.filter(post=post).count()


class FeedCommentsView(generics.CreateAPIView):
    """POST /api/posts/{id}/comments"""

    serializer_class = CommentSerializer
    throttle_scope = "user"

    def perform_create(self, serializer):
        post = Post.objects.get(pk=self.kwargs["pk"])
        comment = serializer.save(author=self.request.user, post=post)
        # Mention notifications
        notify_mention(comment.content, self.request.user, post=post)
        if post.author != self.request.user and post.author.notify_comments:
            notify(post.author, "NEW COMMENT ON YOUR TRANSMISSION", post=post, kind="comment")


class PollVoteView(generics.CreateAPIView):
    serializer_class = PollVoteSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class FollowView(generics.GenericAPIView):
    """POST /api/users/{username}/follow"""

    def post(self, request, username):
        from django.contrib.auth import get_user_model

        target = get_user_model().objects.filter(username=username, is_active=True).first()
        if not target:
            return Response({"detail": "NOT_FOUND"}, status=status.HTTP_404_NOT_FOUND)
        if target == request.user:
            return Response({"detail": "CANNOT_FOLLOW_SELF"}, status=status.HTTP_400_BAD_REQUEST)
        follow, created = Follow.objects.get_or_create(follower=request.user, following=target)
        if not created:
            follow.delete()
        if created and target.notify_followers:
            notify(target, f"NEW FOLLOWER: {request.user.username}", kind="follower")
        return Response({"following": bool(created)})


class FeedView(generics.ListAPIView):
    """GET /api/feed — posts from followed users + own."""

    serializer_class = PostSerializer

    def get_queryset(self):
        from django.contrib.auth import get_user_model

        User = get_user_model()
        followed = Follow.objects.filter(follower=self.request.user).values_list("following_id", flat=True)
        qs = Post.objects.filter(is_deleted=False, author_id__in=[self.request.user.pk] + list(followed))
        qs = annotate_post_queryset(qs, self.request.user)
        return qs.select_related("author").order_by("-created_at")