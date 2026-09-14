"""File-type validation using MIME sniffing, not just extensions."""

import hashlib
import io

import filetype

# Known-safe categories and the signature-based type families we accept.
# Files that don't match get put in "application/octet-stream" and are allowed
# only for owners (download/delete). Executables are blocked outright.
EXECUTABLE_MIMES = {
    "application/x-msdownload",
    "application/x-msdos-program",
    "application/x-dosexec",
    "application/x-executable",
    "application/x-sh",
    "application/vnd.microsoft.portable-executable",
    "text/x-script.python",
}

# Double-block extensions regardless of reported MIME.
BLOCKED_EXTENSIONS = {"exe", "bat", "cmd", "scr", "com", "pif", "msi", "sh", "php", "cgi", "pl", "py", "pyc", "so", "dll", "dylib", "apk", "jar", "vbs", "js"}


def sha256_of(chunked_file):
    h = hashlib.sha256()
    for chunk in chunked_file.chunks():
        h.update(chunk)
    return h.hexdigest()


def inspect_file(file_obj):
    """Validate a file, extracting MIME + category.

    Returns (category, detected_mime) or raises ValueError for dangerous files.
    """
    file_obj.seek(0)
    kind = filetype.guess(file_obj)

    ext = (getattr(file_obj, "name", "") or "").rsplit(".", 1)[-1].lower()
    if ext in BLOCKED_EXTENSIONS:
        raise ValueError("FILE_TYPE_BLOCKED")

    if kind is not None:
        mime = kind.mime
        ext_guess = kind.extension
    else:
        mime = "application/octet-stream"
        ext_guess = ""

    if mime in EXECUTABLE_MIMES:
        raise ValueError("FILE_TYPE_BLOCKED")

    category = categorize(mime)
    if category == "image" and mime not in ("image/jpeg", "image/png", "image/gif", "image/webp", "image/bmp"):
        raise ValueError("FILE_TYPE_BLOCKED")

    file_obj.seek(0)
    return category, mime, ext_guess


def categorize(mime):
    if mime.startswith("image/"):
        return "image"
    if mime.startswith("video/"):
        return "video"
    if mime.startswith("audio/"):
        return "audio"
    if mime in (
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-powerpoint",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "text/plain",
        "text/markdown",
        "text/csv",
    ):
        return "document"
    if mime in ("application/zip", "application/x-rar-compressed", "application/gzip", "application/x-7z-compressed", "application/x-tar"):
        return "archive"
    return "other"