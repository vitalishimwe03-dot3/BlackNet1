from django.urls import path
from rest_framework.routers import SimpleRouter

from posts.views import PostViewSet, FeedView, FeedCommentsView, PollVoteView

router = SimpleRouter()
router.register("", PostViewSet, basename="posts")

urlpatterns = router.urls + [
    path("feed", FeedView.as_view(), name="posts_feed"),
    path("<uuid:pk>/comments", FeedCommentsView.as_view(), name="posts_comments"),
    path("<uuid:pk>/vote", PollVoteView.as_view(), name="posts_vote"),
]