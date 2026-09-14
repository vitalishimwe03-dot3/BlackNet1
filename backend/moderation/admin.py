from django.contrib import admin
from .models import Report, AuditLog


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("category", "target_type", "target_id", "status", "reporter", "created_at")
    list_filter = ("category", "target_type", "status")
    search_fields = ("reporter__username", "target_id")


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("user", "action", "target_type", "target_id", "created_at")
    list_filter = ("action",)
    search_fields = ("user__username", "action")