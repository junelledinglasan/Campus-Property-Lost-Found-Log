import base64
import binascii
import mimetypes
import uuid

from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.fields import SkipField

ALLOWED_PREFIXES = {
    'data:image/jpeg;base64,': 'jpg',
    'data:image/png;base64,': 'png',
    'data:image/webp;base64,': 'webp',
}
MAX_PHOTO_BYTES = 5 * 1024 * 1024


class Base64ImageField(serializers.ImageField):
    """Tumatanggap ng larawan bilang data URL (ganito ipinapadala ng frontend).

    - data URL: bagong larawan. Sinusuri kung totoong larawan at hindi lalampas sa 5 MB.
    - ibang string (hal. ang URL na ibinalik ng API): walang pagbabago.
    - null: aalisin ang larawan.
    Ang ibinabalik na value ay ang URL ng larawan (para sa public na larawan ng item).
    """

    default_error_messages = {
        'invalid_image': 'That file is not a readable image. Use a JPG, PNG, or WebP photo.',
        'too_large': 'The photo is too large. Use an image under 5 MB.',
    }

    def to_internal_value(self, data):
        if isinstance(data, str):
            extension = None
            for prefix, ext in ALLOWED_PREFIXES.items():
                if data.startswith(prefix):
                    extension = ext
                    payload = data[len(prefix):]
                    break
            if extension is None:
                if data.startswith('data:'):
                    self.fail('invalid_image')
                raise SkipField()  # URL ng kasalukuyang larawan: huwag galawin
            try:
                raw = base64.b64decode(''.join(payload.split()), validate=True)
            except (binascii.Error, ValueError):
                self.fail('invalid_image')
            if len(raw) > MAX_PHOTO_BYTES:
                self.fail('too_large')
            data = ContentFile(raw, name=f'{uuid.uuid4().hex}.{extension}')
        return super().to_internal_value(data)

    def to_representation(self, value):
        if not value:
            return None
        return value.url


class HandoverPhotoField(serializers.Field):
    """Para sa handover photo: nakatago sa private storage, kaya ibinabalik bilang data URL
    at para lang sa OSAS staff (staff-only ang endpoint na gumagamit nito)."""

    def to_representation(self, value):
        if not value:
            return None
        try:
            with value.open('rb') as handle:
                raw = handle.read()
        except (FileNotFoundError, OSError, ValueError):
            return None
        mime = mimetypes.guess_type(value.name)[0] or 'image/jpeg'
        return f'data:{mime};base64,{base64.b64encode(raw).decode("ascii")}'
