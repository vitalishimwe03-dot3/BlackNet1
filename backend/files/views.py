import secrets
import uuid

from django.conf import settings
from django.db.models import Q
from django.utils import timezone
from rest_framework import viewsets, generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.throttling import ScopedRateThrottle

from notifications.services import notify
from security.models import SecurityEvent
from .models import File, Folder, ShareLink, StorageUsage
from .serializers import (
    FileSerializer,
    FolderSerializer,
    StorageUsageSerializer,
    CreateShareLinkSerializer,
    UploadSerializer,
)
from .services import can_upload, recalculate_storage
from .validation import inspect_file


class FolderViewSet(viewsets.ModelViewSet):
    serializer_class = FolderSerializer

    def get_queryset(self):
        return Folder.objects.filter(owner=self.request.user).order_by("name")

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def perform_update(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=False, methods=["get"])
    def tree(self, request):
        folders = Folder.objects.filter(owner=request.user).values("id", "parent_id", "name")
        return Response(list(folders))


class FileViewSet(viewsets.ModelViewSet):
    """File explorer. Upload, list, download, rename, delete, search, sort."""

    serializer_class = FileSerializer
    parser_classes = [MultiPartParser, FormParser]
    throttle_scope = "uploads"

    def get_queryset(self):
        qs = File.objects.filter(owner=self.request.user)
        folder = self.request.query_params.get("folder", "")
        if folder and folder != "root":
            qs = qs.filter(folder_id=folder)
        elif folder == "root":
            qs = qs.filter(folder__isnull=True)

        vault = self.request.query_params.get("vault", "")
        if vault == "true":
            qs = qs.filter(in_vault=True)
        elif vault == "false":
            qs = qs.filter(in_vault=False)

        search = self.request.query_params.get("q")
        if search:
            qs = qs.filter(original_name__icontains=search)

        category = self.request.query_params.get("category")
        if category:
            qs = qs.filter(category=category)

        sort = self.request.query_params.get("sort", "created_at")
        order = self.request.query_params.get("order", "desc")
        if order == "asc":
            sort = sort
        field_map = {
            "name": "original_name",
            "size": "size_bytes",
            "created": "created_at",
            "accessed": "last_accessed",
            "created_at": "created_at",
        }
        field = field_map.get(sort, "created_at")
        if order == "asc":
            qs = qs.order_by(field)
        else:
            qs = qs.order_by("-" + field)
        return qs

    def perform_destroy(self, instance):
        # The post_delete signal recalculates the owner's storage usage.
        instance.delete()

    @action(detail=False, methods=["post"])
    def upload(self, request):
        serializer = UploadSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        uploaded = serializer.validated_data["file"]
        if not can_upload(request.user, uploaded.size):
            return Response({"detail": "STORAGE_QUOTA_EXCEEDED"}, status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)

        # MIME sniffing + dangerous-file blocking
        try:
            category, mime, _ext = inspect_file(uploaded)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        folder_id = request.data.get("folder")
        folder = Folder.objects.filter(id=folder_id, owner=request.user).first() if folder_id else None
        in_vault = request.data.get("in_vault") in ("true", "True", "1", "on")

        # NOTE: rendered media is served directly; uploaded executables are
        # blocked above, and safe files are stored with randomized names so
        # nothing user-controlled lives in an executable location.
        original_name = getattr(uploaded, "_name", None) or uploaded.name.split("/")[-1]
        stored_name = f"uploads/{request.user.pk}/{uuid.uuid4().hex}"
        uploaded.name = stored_name

        try:
            file_record = File.objects.create(
                owner=request.user,
                folder=folder,
                original_name=original_name,
                stored_name=stored_name,
                file=uploaded,
                size_bytes=uploaded.size,
                content_type=mime,
                category=category,
                in_vault=in_vault,
            )
        except Exception:
            return Response({"detail": "UPLOAD_FAILED"}, status=status.HTTP_400_BAD_REQUEST)

        recalculate_storage(request.user)

        from files.tasks import process_file
        try:
            process_file.delay(str(file_record.pk))
        except Exception:
            pass

        SecurityEvent.objects.create(user=request.user, event_type="FILE_UPLOADED")

        if request.user.notify_security:
            notify(request.user, "FILE UPLOADED AND INDEXED", kind="system", file=file_record)

        return Response(
            FileSerializer(file_record, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"])
    def rename(self, request, pk=None):
        file = self.get_object()
        new_name = (request.data.get("name") or "").strip()
        if not new_name:
            return Response({"detail": "NAME_REQUIRED"}, status=status.HTTP_400_BAD_REQUEST)
        file.original_name = new_name[:255]
        file.save(update_fields=["original_name"])
        return Response(FileSerializer(file, context={"request": request}).data)

    @action(detail=True, methods=["post"])
    def move(self, request, pk=None):
        file = self.get_object()
        folder_id = request.data.get("folder")
        if folder_id and folder_id not in ("", "root", "null", "None"):
            folder = Folder.objects.filter(id=folder_id, owner=request.user).first()
            if not folder:
                return Response({"detail": "FOLDER_NOT_FOUND"}, status=status.HTTP_404_NOT_FOUND)
            file.folder = folder
        else:
            file.folder = None
        file.save(update_fields=["folder"])
        return Response(FileSerializer(file, context={"request": request}).data)

    @action(detail=True, methods=["get"])
    def download(self, request, pk=None):
        file = self.get_object()
        file.last_accessed = timezone.now()
        file.save(update_fields=["last_accessed"])
        return Response({"url": FileSerializer(file, context={"request": request}).data["url"]})

    @action(detail=False, methods=["get"])
    def usage(self, request):
        usage, _ = StorageUsage.objects.get_or_create(user=request.user)
        return Response(StorageUsageSerializer(usage, context={"storage": usage, "request": request}).data)


class ShareLinkView(generics.GenericAPIView):
    """POST /api/files/{pk}/share — create a temporary share link for a file the user owns."""

    def post(self, request, pk=None):
        file = File.objects.filter(pk=pk, owner=request.user).first()
        if not file:
            return Response({"detail": "NOT_FOUND"}, status=status.HTTP_404_NOT_FOUND)

        serializer = CreateShareLinkSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        expires_at = None
        if data.get("expires_hours"):
            expires_at = timezone.now() + timezone.timedelta(hours=data["expires_hours"])

        password_hashed = ""
        if data.get("password"):
            from django.contrib.auth.hashers import make_password
            password_hashed = make_password(data["password"])

        token = secrets.token_urlsafe(9).replace("-", "").replace("_", "")[:8].upper()
        link = ShareLink.objects.create(
            file=file,
            created_by=request.user,
            token=token,
            password=password_hashed,
            expires_at=expires_at,
            max_downloads=data.get("max_downloads"),
        )
        share_url = request.build_absolute_uri(f"/api/files/share/{link.token}")
        return Response({"token": token, "url": share_url, "expires_at": expires_at})

    def get(self, request, token=None, pk=None):
        return Response({"ok": True, "detail": "USE POST WITH PASSWORD"})


class PublicShareView(generics.GenericAPIView):
    """POST /api/files/share/{token} — password-protected, expiring, count-limited download."""

    permission_classes = []
    authentication_classes = []

    def post(self, request, token):
        link = ShareLink.objects.filter(token=token.upper()).select_related("file").first()
        if not link or not link.can_download():
            return Response({"detail": "LINK_EXPIRED"}, status=status.HTTP_410_GONE)

        if link.password:
            from django.contrib.auth.hashers import check_password
            password = request.data.get("password", "")
            if not check_password(password, link.password):
                return Response({"detail": "INVALID_PASSWORD"}, status=status.HTTP_403_FORBIDDEN)

        link.download_count += 1
        link.save(update_fields=["download_count"])

        file = link.file
        file.last_accessed = timezone.now()
        file.save(update_fields=["last_accessed"])

        return Response({"url": file.file.url, "name": file.original_name})