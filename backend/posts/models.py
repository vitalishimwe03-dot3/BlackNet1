import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class Post(models.Model):
    """A feed post: text, image, video, link, poll or file attachment."""

    POST_TYPES = [
        ("text", "Text"),
        ("image", "Image"),
        ("video", "Video"),
        ("link", "Link"),
        ("poll", "Poll"),
        ("file", "File"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts")
    content = models.TextField(max_length=10000, blank=True, default="")
    post_type = models.CharField(max_length=16, choices=POST_TYPES, default="text")
    community = models.ForeignKey(
        "communities.Community", on_delete=models.CASCADE, null=True, blank=True, related_name="posts"
    )
    image = models.ImageField(upload_to="posts/images/", null=True, blank=True)
    video = models.FileField(upload_to="posts/videos/", null=True, blank=True)
    file = models.ForeignKey("files.File", on_delete=models.SET_NULL, null=True, blank=True, related_name="posts")
    link_url = models.URLField(null=True, blank=True)
    poll_data = models.JSONField(null=True, blank=True)

    view_count = models.IntegerField(default=0)
    is_edited = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["author", "-created_at"]),
            models.Index(fields=["community", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.author.username}: {self.content[:40] or self.post_type}"


class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments")
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies")
    content = models.TextField(max_length=4000)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.author.username}: {self.content[:40]}"


class Like(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="likes")
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="likes", null=True, blank=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "post"], name="uniq_user_post_like")]
        indexes = [models.Index(fields=["post", "created_at"])]

    def __str__(self):
        return f"{self.user} liked {self.post or self.comment}"


class Follow(models.Model):
    follower = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="following")
    following = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="followers")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["follower", "following"], name="uniq_follow_pair")]

    def __str__(self):
        return f"{self.follower} -> {self.following}"


class Bookmark(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookmarks")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="bookmarked_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "post"], name="uniq_bookmark")]


class PollVote(models.Model):
    poll = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="poll_votes")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    choice = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["poll", "user"], name="uniq_poll_vote")]