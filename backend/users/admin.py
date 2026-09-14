from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

from .models import User, UserProfile, UserSession


@admin.register(User)
class BlackNetUserAdmin(UserAdmin):
    list_display = ("username", "email", "is_active", "is_2fa_enabled", "storage_bytes_used", "last_active", "is_online")
    list_filter = ("is_active", "is_2fa_enabled", "is_staff", "profile_visibility")
    search_fields = ("username", "email")
    readonly_fields = ("id", "created_at", "last_active", "storage_bytes_used", "storage_bytes_total")
    fieldsets = UserAdmin.fieldsets + (
        ("Privacy & Notifications", {
            "fields": ("profile_visibility", "notify_new_messages", "notify_likes", "notify_comments"),
        }),
        ("2FA", {"fields": ("is_2fa_enabled", "two_factor_secret")}),
        ("Storage", {"fields": ("storage_bytes_total", "storage_bytes_used")}),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "display_name", "reputation")
    search_fields = ("user__username", "display_name")


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ("user", "device_name", "ip_address", "is_current", "last_seen")
    list_filter = ("is_current", "revoked_at")
    search_fields = ("user__username",)