from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminUser(BasePermission):
    """
    Allows access only to admin users.
    """

    def has_permission(self, request, view):
        # Allow safe methods
        if request.method in SAFE_METHODS:
            return True
        
        return bool(
            request.user and request.user.is_authenticated
              and request.user.role == 'admin'
        )

class IsUserOrAdmin(BasePermission):
    """
    Allows access to the user themselves or admin users.
    """

    def has_permission(self, request, view):       
        return bool(
            request.user and request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        # Allow safe methods
        if request.method in SAFE_METHODS:
            return True
        
        return bool(
            request.user and request.user.is_authenticated
              and (request.user.role == 'admin' or getattr(obj, 'user', None) == request.user)
        )
