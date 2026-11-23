from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import APIException, NotAuthenticated, Throttled
from rest_framework.views import exception_handler


class Conflict(APIException):
    """Hindi na pwede ang aksyon dahil iba na ang kasalukuyang estado (hal. na-claim na ang item)."""

    status_code = status.HTTP_409_CONFLICT
    default_detail = 'This action is no longer possible.'
    default_code = 'conflict'


def _first_message(data):
    """Kinukuha ang unang mensahe sa kahit anong hugis ng error data."""
    if isinstance(data, dict):
        if 'detail' in data:
            return _first_message(data['detail'])
        for value in data.values():
            return _first_message(value)
        return ''
    if isinstance(data, (list, tuple)):
        return _first_message(data[0]) if data else ''
    return str(data)


def api_exception_handler(exc, context):
    """Lahat ng error ay {"detail": "isang malinaw na mensahe"}, para madaling ipakita ng frontend."""
    response = exception_handler(exc, context)
    if response is None:
        return None

    if isinstance(exc, NotAuthenticated):
        message = 'Sign in as OSAS staff to do this.'
    elif isinstance(exc, Throttled):
        message = 'Too many attempts. Wait a few minutes and try again.'
    elif isinstance(exc, Http404) or response.status_code == status.HTTP_404_NOT_FOUND:
        message = _first_message(response.data)
        if message.startswith('No ') or message == 'Not found.':
            message = 'This item does not exist or was removed.'
    else:
        message = _first_message(response.data)

    response.data = {'detail': message}
    return response
