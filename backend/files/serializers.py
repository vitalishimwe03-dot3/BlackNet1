from rest_framework import serializers
from django.conf import settings

from .models import File, Folder, ShareLink, StorageUsage
from .services import can_upload, available_bytes


class FileSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    share_url = serializers.SerializerMethodField()

    class Meta:
        model = File
        fields = [
            "id", "owner", "folder", "original_name", "stored_name",
            "size_bytes", "content_type", "category", "sha256",
            "is_processed", "thumbnail", "width", "height", "duration_seconds",
            "in_vault", "last_accessed", "created_at",
            "url", "thumbnail_url", "share_url",
        ]
        read_only_fields = [
            "id", "owner", "stored_name", "size_bytes", "content_type",
            "category", "sha256", "is_processed", "thumbnail",
            "width", "height", "duration_seconds", "created_at", "url", "share_url",
        ]

    def get_url(self, obj):
        request = self.context.get("request")
        if not request or obj.owner != request.user:
            return None
        from files.storage import storage_url
        return storage_url(obj.file.name)

    def get_thumbnail_url(self, obj):
        if obj.thumbnail:
            from files.storage import storage_url
            return storage_url(obj.thumbnail.name)
        return None

    def get_share_url(self, obj):
        request = self.context.get("request")
        if not request or obj.owner != request.user:
            return None
        link = obj.share_links.filter(is_active=True).first()
        return f"{request.build_absolute_uri('/')}api/files/share/{link.token}" if link else None


class FolderSerializer(serializers.ModelSerializer):
    file_count = serializers.SerializerMethodField()

    class Meta:
        model = Folder
        fields = ["id", "owner", "parent", "name", "created_at", "file_count"]
        read_only_fields = ["id", "owner", "created_at"]

    def get_file_count(self, obj):
        return obj.files.count()

    def validate(self, attrs):
        owner = self.context["request"].user
        parent = attrs.get("parent")
        name = attrs.get("name", "")
        qs = Folder.objects.filter(owner=owner, parent=parent, name=name)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError({"name": "FOLDER_EXISTS"})
        return attrs


class StorageUsageSerializer(serializers.ModelSerializer):
    free_bytes = serializers.SerializerMethodField()

    class Meta:
        model = StorageUsage
        fields = [
            "total_bytes", "used_bytes", "free_bytes",
            "image_bytes", "video_bytes", "document_bytes",
            "audio_bytes", "archive_bytes", "other_bytes",
            "file_count", "updated_at",
        ]

    def get_free_bytes(self, obj):
        storage = self.context.get("storage")
        if storage and getattr(storage, "user", None):
            return available_bytes(storage.user)
        return max(0, obj.total_bytes - obj.used_bytes)


class CreateShareLinkSerializer(serializers.Serializer):
    expires_hours = serializers.IntegerField(required=False, min_value=1, max_value=72)
    max_downloads = serializers.IntegerField(required=False, min_value=1, max_value=1000)
    password = serializers.CharField(required=False, allow_blank=True, max_length=128)


class UploadSerializer(serializers.Serializer):
    file = serializers.FileField(required=False)
    folder = serializers.UUIDField(required=False)
    in_vault = serializers.BooleanField(required=False, default=False)

    def validate(self, attrs):
        request = self.context["request"]
        file = attrs.get("file")
        if not file:
            raise serializers.ValidationError({"file": "FILE_REQUIRED"})
        if file.size <= 0:
            raise serializers.ValidationError({"file": "EMPTY_FILE"})
        if not can_upload(request.user, file.size):
            raise serializers.ValidationError({"file": "QUOTA_EXCEEDED"})
        return attrs