from django.contrib import admin
from .models import Post, Comment, Like, Follow, Bookmark, PollVote


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("author", "post_type", "view_count", "is_deleted", "created_at")
    list_filter = ("post_type", "is_deleted")
    search_fields = ("content", "author__username")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("author", "post", "is_deleted", "created_at")
    search_fields = ("content",)


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ("user", "post", "created_at")


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ("follower", "following", "created_at")


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ("user", "post")


@admin.register(PollVote)
class PollVoteAdmin(admin.ModelAdmin):
    list_display = ("user", "poll", "choice")