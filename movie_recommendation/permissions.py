from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    """
    Anyone can read.
    Only admins can create, update, or delete.
    """
    message = "You can view this, but only an admin can change it."

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        return bool(
            request.user and request.user.is_authenticated
            and getattr(request.user, "role", None) == "admin"
        )


class IsAuthenticatedOwnerOrAdmin(BasePermission):
    """
    Only authenticated users can access.
    Admins can access any object.
    Owners can access their own object.
    """
    message = "You do not have permission to access this item."

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False

        if getattr(request.user, "role", None) == "admin":
            return True

        user_pk = view.kwargs.get("user_pk")

        if user_pk is not None:
            return str(request.user.id) == str(user_pk)

        return True

    def has_object_permission(self, request, view, obj):
        if not (request.user and request.user.is_authenticated):
            return False

        if getattr(request.user, "role", None) == "admin":
            return True

        if obj == request.user:
            return True

        owner = getattr(obj, "user", None)
        return owner == request.user
