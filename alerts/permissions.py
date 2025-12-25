from rest_framework import permissions


class AlertPermission(permissions.BasePermission):
    """
    Custom permission for alerts:
    - Admin: full access (create, read, update, delete, PATCH)
    - Analyst: read-only access (GET, HEAD, OPTIONS only)
    """

    def has_permission(self, request, view):
        """Check if user has permission for the view action"""
        if not request.user or not request.user.is_authenticated:
            return False

        # Admin has full access including PATCH
        if request.user.groups.filter(name='Admin').exists():
            return True

        # Analyst has read-only access (SAFE_METHODS only)
        # PATCH is not a safe method, so Analyst will get 403 Forbidden
        if request.user.groups.filter(name='Analyst').exists():
            return request.method in permissions.SAFE_METHODS

        # Other authenticated users have no access
        return False

    def has_object_permission(self, request, view, obj):
        """Check if user has permission for the specific object"""
        # Same logic as has_permission for consistency
        return self.has_permission(request, view)
