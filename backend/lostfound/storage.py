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
    return PrivateStorage()
