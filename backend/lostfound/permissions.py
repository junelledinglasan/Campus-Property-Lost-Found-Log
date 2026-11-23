from rest_framework.permissions import BasePermission


class IsStaff(BasePermission):
    """OSAS staff lang: naka-sign in at may is_staff."""

    message = 'Sign in as OSAS staff to do this.'

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.is_staff)
