from django.contrib import admin
from .models import File, Folder, StorageUsage, ShareLink


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ("original_name", "owner", "category", "size_bytes", "created_at")
    list_filter = ("category", "in_vault")
    search_fields = ("original_name", "owner__username")


@admin.register(Folder)
class FolderAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "parent", "created_at")


@admin.register(StorageUsage)
class StorageUsageAdmin(admin.ModelAdmin):
    list_display = ("user", "used_bytes", "total_bytes", "file_count", "updated_at")


@admin.register(ShareLink)
class ShareLinkAdmin(admin.ModelAdmin):
    list_display = ("file", "token", "is_active", "expires_at", "download_count")