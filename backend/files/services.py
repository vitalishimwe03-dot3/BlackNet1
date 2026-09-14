"""Storage accounting helpers. All quota math in bytes for precision."""

from django.db import transaction
from django.utils import timezone

from .models import File, StorageUsage


def recalculate_storage(user):
    """Recompute the user's storage usage from actual file rows.

    Safe to call any time; used after deletions/size changes. Runs in a
    transaction to keep the counters consistent with the file table.
    """
    with transaction.atomic():
        aggregations = File.objects.filter(owner=user).values("category")
        counts = {}
        sizes = {}
        for row in File.objects.filter(owner=user):
            cat = row.category
            sizes[cat] = sizes.get(cat, 0) + row.size_bytes
            counts[cat] = counts.get(cat, 0) + 1

        total_used = sum(sizes.values())
        total_files = sum(counts.values())

        usage, _ = StorageUsage.objects.get_or_create(user=user)
        usage.total_bytes = user.storage_bytes_total
        usage.used_bytes = total_used
        usage.image_bytes = sizes.get("image", 0)
        usage.video_bytes = sizes.get("video", 0)
        usage.document_bytes = sizes.get("document", 0)
        usage.audio_bytes = sizes.get("audio", 0)
        usage.archive_bytes = sizes.get("archive", 0)
        usage.other_bytes = sizes.get("other", 0)
        usage.file_count = total_files
        usage.save()

        user.storage_bytes_used = total_used
        user.save(update_fields=["storage_bytes_used"])

    return usage


def available_bytes(user):
    return max(0, user.storage_bytes_total - user.storage_bytes_used)


def can_upload(user, size_bytes):
    return available_bytes(user) >= size_bytes