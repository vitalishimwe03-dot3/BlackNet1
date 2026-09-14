"""Storage abstraction: local filesystem or S3-compatible storage.

Kept deliberately thin so production can swap backends via settings without
changing calling code.
"""
from django.conf import settings
from django.core.files.storage import default_storage


def storage_backend():
    """Return the configured default storage backend."""
    return default_storage


def storage_url(name):
    return default_storage.url(name)


def file_exists(name):
    return default_storage.exists(name)


def absolute_path(name):
    """Local filesystem path for a stored file (only meaningful for local storage)."""
    return default_storage.path(name)