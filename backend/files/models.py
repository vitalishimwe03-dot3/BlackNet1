import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class Folder(models.Model):
    """A per-user virtual folder for file organization."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="folders")
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="children")
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [["owner", "parent", "name"]]
        indexes = [models.Index(fields=["owner", "parent"])]

    def __str__(self):
        return self.name


class File(models.Model):
    """File record enforcing the per-user storage quota."""

    CATEGORY_CHOICES = [
        ("image", "Image"),
        ("video", "Video"),
        ("document", "Document"),
        ("audio", "Audio"),
        ("archive", "Archive"),
        ("other", "Other"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="files")
    folder = models.ForeignKey(Folder, on_delete=models.SET_NULL, null=True, blank=True, related_name="files")
    original_name = models.CharField(max_length=255)
    stored_name = models.CharField(max_length=255)
    file = models.FileField(upload_to="uploads/", max_length=500)
    size_bytes = models.BigIntegerField(default=0)
    content_type = models.CharField(max_length=120, default="application/octet-stream")
    category = models.CharField(max_length=16, choices=CATEGORY_CHOICES, default="other")
    sha256 = models.CharField(max_length=64, blank=True, default="")
    is_processed = models.BooleanField(default=False)

    # Thumbnails / previews
    thumbnail = models.ImageField(upload_to="thumbnails/", null=True, blank=True)
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    duration_seconds = models.FloatField(null=True, blank=True)

    # Vault (protected area)
    in_vault = models.BooleanField(default=False)

    last_accessed = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["owner", "created_at"]),
            models.Index(fields=["owner", "folder"]),
            models.Index(fields=["owner", "category"]),
        ]

    def __str__(self):
        return self.original_name

    def delete(self, *args, **kwargs):
        import django.core.files.storage
        from files.storage import storage_backend

        storage = storage_backend()
        try:
            if self.file:
                storage.delete(self.file.name)
            if self.thumbnail:
                storage.delete(self.thumbnail.name)
        except Exception:
            pass
        return super().delete(*args, **kwargs)


class StorageUsage(models.Model):
    """Snapshot of per-user storage accounting (from files)."""

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="storage_usage")
    total_bytes = models.BigIntegerField(default=settings.DEFAULT_USER_STORAGE_BYTES)
    used_bytes = models.BigIntegerField(default=0)
    image_bytes = models.BigIntegerField(default=0)
    video_bytes = models.BigIntegerField(default=0)
    document_bytes = models.BigIntegerField(default=0)
    audio_bytes = models.BigIntegerField(default=0)
    archive_bytes = models.BigIntegerField(default=0)
    other_bytes = models.BigIntegerField(default=0)
    file_count = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}: {self.used_bytes}/{self.total_bytes}"


class ShareLink(models.Model):
    """Temporary, revocable secure link granting time-limited access to a file."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.ForeignKey(File, on_delete=models.CASCADE, related_name="share_links")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="share_links")
    token = models.CharField(max_length=16, unique=True, help_text="Short share code like 7F92A")
    password = models.CharField(max_length=255, blank=True, default="", help_text="Optionally PBKDF2-hashed password")
    expires_at = models.DateTimeField(null=True, blank=True)
    max_downloads = models.IntegerField(null=True, blank=True)
    download_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["token"])]

    @property
    def is_expired(self):
        return bool(self.expires_at and self.expires_at < timezone.now())

    @property
    def is_user_action(self):
        return bool(self.password) or True

    def can_download(self):
        if not self.is_active or self.is_expired:
            return False
        if self.max_downloads is not None and self.download_count >= self.max_downloads:
            return False
        return True