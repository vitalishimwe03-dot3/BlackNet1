"""Celery tasks for background file processing (thumbnails, metadata)."""

from celery import shared_task
from django.core.files import File as DjangoFile
from django.db import models

from .models import File


@shared_task
def process_file(file_id):
    """Generate thumbnails/previews and video duration asynchronously."""
    file = File.objects.filter(pk=file_id).first()
    if not file:
        return

    try:
        if file.category == "image":
            _make_image_thumbnail(file)
        elif file.category == "video":
            _probe_video(file)
        file.is_processed = True
        file.save(update_fields=["is_processed"])
    except Exception:
        # Background failure must never break the upload flow.
        pass


def _make_image_thumbnail(file):
    from io import BytesIO

    from PIL import Image, ImageOps

    try:
        file.file.seek(0)
        img = Image.open(file.file)
        img.load()
        file.width, file.height = img.size

        img.thumbnail((480, 480), Image.LANCZOS)
        thumb = ImageOps.exif_transpose(img)
        buf = BytesIO()
        thumb.save(buf, format="JPEG", quality=80)
        buf.seek(0)

        from django.core.files.storage import default_storage

        thumb_name = f"thumbnails/{file.owner_id}/{file.pk}.jpg"
        default_storage.save(thumb_name, DjangoFile(buf, name=thumb_name))
        # The model's ImageField expects a name relative to MEDIA_ROOT for local storage.
        try:
            file.thumbnail = thumb_name
        except Exception:
            file.thumbnail.name = thumb_name

        file.save(update_fields=["width", "height", "thumbnail"])
    except Exception:
        return


def _probe_video(file):
    """Extract duration/resolution via mutagen or ffprobe if available.

    FFmpeg is optional in dev; in production the deployment can add it and set
    ``BLACKNET_ENABLE_FFMPEG=1``. This keeps the worker non-fragile.
    """
    import os
    import subprocess

    from .storage import absolute_path

    path = absolute_path(file.file.name)
    if not os.path.exists(path):
        return
    ffprobe = os.getenv("FFPROBE_PATH", "ffprobe")
    try:
        result = subprocess.run(
            [ffprobe, "-v", "error", "-select_streams", "v:0",
             "-show_entries", "stream=width,height,duration",
             "-of", "csv=p=0", path],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0 and result.stdout.strip():
            parts = result.stdout.strip().split(",")
            if len(parts) >= 3:
                file.width = int(parts[0])
                file.height = int(parts[1])
                file.duration_seconds = float(parts[2])
                file.save(update_fields=["width", "height", "duration_seconds"])
    except Exception:
        return


@shared_task
def purge_expired_share_links():
    from datetime import timedelta
    from django.utils import timezone

    from .models import ShareLink

    ShareLink.objects.filter(expires_at__lt=timezone.now(), is_active=True).update(is_active=False)


@shared_task
def compute_storage_usage(user_id):
    from django.contrib.auth import get_user_model
    from .services import recalculate_storage

    user = get_user_model().objects.get(pk=user_id)
    recalculate_storage(user)


@shared_task
def validate_stale_files(days=180):
    """Found by Storage Intelligence: report files not accessed in N days.

    Returns recommendations for the dashboard. Non-destructive.
    """
    from datetime import timedelta
    from django.utils import timezone

    cutoff = timezone.now() - timedelta(days=days)
    stale = File.objects.filter(last_accessed__lt=cutoff).values("owner_id").annotate(
        count=models.Count("id")
    )
    return list(stale)