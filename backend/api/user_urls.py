from django.urls import path

from users.views import (
    MeView,
    ProfileView,
    ProfileUpdateView,
    SessionsView,
    RevokeSessionView,
    UserListView,
)
from posts.views import FollowView

urlpatterns = [
    path("me", MeView.as_view(), name="users_me"),
    path("me/profile", ProfileUpdateView.as_view(), name="users_me_profile"),
    path("me/sessions", SessionsView.as_view(), name="users_sessions"),
    path("me/sessions/<uuid:pk>/revoke", RevokeSessionView.as_view(), name="users_revoke_session"),
    path("", UserListView.as_view(), name="users_list"),
    path("<str:username>", ProfileView.as_view(), name="users_detail"),
    path("<str:username>/follow", FollowView.as_view(), name="users_follow"),
]