from django.apps import AppConfig


class FilesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "files"

    def ready(self):
        from . import signals  # noqa: F401
        from . import tasks  # noqa: F401