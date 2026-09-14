from django.urls import path, include
from rest_framework.routers import DefaultRouter

from communities.views import CommunityViewSet, CommunityChannelViewSet, CommunityPostsView

router = DefaultRouter()
router.register("", CommunityViewSet, basename="communities")

urlpatterns = router.urls + [
    path("<uuid:pk>/posts", CommunityPostsView.as_view(), name="community_posts"),
    path("<uuid:community_pk>/channels", CommunityChannelViewSet.as_view({"get": "list", "post": "create"}), name="community_channels"),
]