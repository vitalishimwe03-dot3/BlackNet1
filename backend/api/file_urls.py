from django.urls import path
from rest_framework.routers import SimpleRouter

from files.views import FileViewSet, FolderViewSet, ShareLinkView, PublicShareView

router = SimpleRouter()
router.register("", FileViewSet, basename="files")
router.register("folders", FolderViewSet, basename="folders")

urlpatterns = router.urls + [
    path("<uuid:pk>/share", ShareLinkView.as_view(), name="files_share"),
    path("share/<str:token>", PublicShareView.as_view(), name="files_share_public"),
]