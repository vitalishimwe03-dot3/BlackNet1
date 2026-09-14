from django.contrib import admin
from .models import SecurityEvent


@admin.register(SecurityEvent)
class SecurityEventAdmin(admin.ModelAdmin):
    list_display = ("user", "event_type", "ip_address", "created_at")
    list_filter = ("event_type",)
    search_fields = ("user__username", "ip_address")
    readonly_fields = ("id", "created_at")