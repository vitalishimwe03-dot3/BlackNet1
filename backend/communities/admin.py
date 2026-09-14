from django.contrib import admin
from .models import Community, CommunityMember, CommunityChannel


@admin.register(Community)
class CommunityAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "visibility", "is_active", "created_at")
    list_filter = ("visibility", "is_active")
    search_fields = ("name", "description")


@admin.register(CommunityMember)
class CommunityMemberAdmin(admin.ModelAdmin):
    list_display = ("user", "community", "role", "is_banned")


@admin.register(CommunityChannel)
class CommunityChannelAdmin(admin.ModelAdmin):
    list_display = ("name", "community")