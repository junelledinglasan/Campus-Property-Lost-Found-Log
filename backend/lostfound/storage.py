import os

from django.conf import settings
from django.core.files.storage import FileSystemStorage


class PrivateStorage(FileSystemStorage):
    """Storage para sa handover photos. Nasa PRIVATE_MEDIA_ROOT ito, hindi sa MEDIA_ROOT,
    kaya walang public na URL. Binabasa ang setting sa bawat gamit para sumunod sa override sa tests."""

    @property
    def base_location(self):
        return settings.PRIVATE_MEDIA_ROOT

    @property
    def location(self):
        return os.path.abspath(self.base_location)


def private_storage():
    """Pribadong bucket sa Supabase kung naka-set, kung hindi ay private_media/ sa disk.
    Sa parehong kaso, walang public na URL ang handover photo."""
    if settings.USE_SUPABASE_STORAGE:
        from storages.backends.s3 import S3Storage
        from .s3options import supabase_s3_options
        return S3Storage(**supabase_s3_options(
            settings.SUPABASE_BUCKET_HANDOVER, settings.SUPABASE_PROJECT_REF,
            settings.SUPABASE_S3_ACCESS_KEY, settings.SUPABASE_S3_SECRET_KEY, settings.SUPABASE_S3_REGION))
    return PrivateStorage()
