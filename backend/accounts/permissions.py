from rest_framework.permissions import SAFE_METHODS, BasePermission


def _is_admin(user):
    return bool(user and user.is_authenticated and (user.is_staff or user.role == "ADMIN"))


class IsSocietyAdmin(BasePermission):
    def has_permission(self, request, view):
        return _is_admin(request.user)


class IsSocietyAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method in SAFE_METHODS:
            return True
        return _is_admin(request.user)
