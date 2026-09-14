"""Command-style global search across people, posts, communities, files."""

from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response

from communities.models import Community
from communities.serializers import CommunitySerializer
from files.models import File
from files.serializers import FileSerializer
from posts.models import Post
from posts.serializers import PostSerializer
from posts.views import annotate_post_queryset
from users.serializers import UserSerializer

USER_MODEL = get_user_model()


class GlobalSearchView(APIView):
    """GET /api/search?q=quantum%20computing"""

    def get(self, request):
        query = (request.query_params.get("q") or "").strip()
        if not query:
            return Response({
                "query": "",
                "users": [],
                "posts": [],
                "communities": [],
                "files": [],
                "total": 0,
            })

        user = request.user

        posts = annotate_post_queryset(
            Post.objects.filter(is_deleted=False, content__icontains=query).select_related("author"),
            user,
        )[:10]

        users = USER_MODEL.objects.filter(
            Q(username__icontains=query) | Q(profile__display_name__icontains=query),
            is_active=True,
            profile_visibility="public",
        ).select_related("profile")[:10]

        communities = Community.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query),
            is_active=True,
        )[:10]

        files = File.objects.filter(owner=user, original_name__icontains=query)[:10]

        return Response({
            "query": query,
            "users": UserSerializer(users, many=True).data,
            "posts": PostSerializer(posts, many=True, context={"request": request}).data,
            "communities": CommunitySerializer(communities, many=True, context={"request": request}).data,
            "files": FileSerializer(files, many=True, context={"request": request}).data,
            "total": len(users) + len(posts) + len(communities) + len(files),
        })