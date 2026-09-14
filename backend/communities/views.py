from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, generics, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from notifications.services import notify
from .models import Community, CommunityMember, CommunityChannel
from .serializers import (
    CommunitySerializer,
    CommunityCreateSerializer,
    CommunityMemberSerializer,
    CommunityChannelSerializer,
)


class CommunityViewSet(viewsets.ModelViewSet):
    """Communities discovery + management. Public communities are browseable."""

    serializer_class = CommunitySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]
    search_fields = ["name", "slug", "description"]
    lookup_field = "pk"

    def get_queryset(self):
        qs = Community.objects.filter(is_active=True)
        visibility = self.request.query_params.get("visibility")
        if visibility == "public":
            qs = qs.filter(visibility="public")
        return qs.order_by("-created_at")

    def get_serializer_class(self):
        if self.action == "create":
            return CommunityCreateSerializer
        return CommunitySerializer

    def perform_create(self, serializer):
        community = serializer.save(owner=self.request.user)
        CommunityMember.objects.create(community=community, user=self.request.user, role="owner")

    @action(detail=True, methods=["post"])
    def join(self, request, pk=None):
        community = self.get_object()
        if community.visibility == "private":
            member = community.members.filter(user=request.user).first()
            if member and not member.is_banned:
                return Response({"detail": "ALREADY_MEMBER"})
            return Response({"detail": "INVITE_REQUIRED"}, status=status.HTTP_403_FORBIDDEN)
        member, created = CommunityMember.objects.get_or_create(community=community, user=request.user)
        if created:
            if community.owner.notify_community:
                notify(community.owner, f"NEW MEMBER JOINED {community.name}", kind="community")
        return Response({"joined": bool(created)})

    @action(detail=True, methods=["post"], url_path="leave")
    def leave(self, request, pk=None):
        community = self.get_object()
        member = community.members.filter(user=request.user).first()
        if member and member.role != "owner":
            member.delete()
        return Response({"detail": "LEFT"})

    @action(detail=True, methods=["get"])
    def members(self, request, pk=None):
        community = self.get_object()
        members = community.members.select_related("user").order_by("joined_at")
        page = self.paginate_queryset(members)
        return self.get_paginated_response(CommunityMemberSerializer(page, many=True).data)

    @action(detail=True, methods=["post"])
    def set_role(self, request, pk=None):
        """Set a member's role (owner/moderator only)."""
        community = self.get_object()
        actor = community.members.filter(user=request.user).first()
        if not actor or actor.role not in ("owner", "moderator"):
            return Response({"detail": "FORBIDDEN"}, status=status.HTTP_403_FORBIDDEN)
        target = community.members.filter(id=request.data.get("member_id")).first()
        new_role = request.data.get("role")
        if not target or new_role not in ("member", "moderator"):
            return Response({"detail": "INVALID_REQUEST"}, status=status.HTTP_400_BAD_REQUEST)
        target.role = new_role
        target.save(update_fields=["role"])
        return Response(CommunityMemberSerializer(target).data)


class CommunityChannelViewSet(viewsets.ModelViewSet):
    serializer_class = CommunityChannelSerializer

    def get_queryset(self):
        return CommunityChannel.objects.filter(community_id=self.kwargs.get("community_pk")).order_by("name")

    def perform_create(self, serializer):
        community = get_object_or_404(Community, pk=self.kwargs.get("community_pk"))
        member = community.members.filter(user=self.request.user).first()
        if not member or member.role not in ("owner", "moderator"):
            return Response({"detail": "FORBIDDEN"}, status=status.HTTP_403_FORBIDDEN)
        serializer.save(community=community)


class CommunityPostsView(generics.ListAPIView):
    from posts.serializers import PostSerializer

    serializer_class = PostSerializer
    pagination_class = None

    def get_queryset(self):
        from posts.models import Post
        from posts.views import annotate_post_queryset

        community = get_object_or_404(Community, pk=self.kwargs["pk"])
        qs = annotate_post_queryset(
            Post.objects.filter(community=community, is_deleted=False).select_related("author"),
            self.request.user,
        )
        return qs.order_by("-created_at")