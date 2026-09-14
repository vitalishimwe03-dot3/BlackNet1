"""BlackNet URL configuration."""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("api.auth_urls")),
    path("api/users/", include("api.user_urls")),
    path("api/posts/", include("api.post_urls")),
    path("api/messages/", include("api.message_urls")),
    path("api/files/", include("api.file_urls")),
    path("api/communities/", include("api.community_urls")),
    path("api/notifications/", include("api.notification_urls")),
    path("api/moderation/", include("api.moderation_urls")),
    path("api/search/", include("api.search_urls")),
    path("api/security/", include("api.security_urls")),
    path("api/schema/", include("api.schema_urls")),
]