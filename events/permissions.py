from rest_framework import permissions


class EventPermission(permissions.BasePermission):
    """
    Custom permission for events:
    - Admin: full access (create, read, update, delete)
    - Analyst: no access (read-only access to alerts only)
    - Other authenticated users: no access
    """

    def has_permission(self, request, view):
        """Check if user has permission for the view action"""
        if not request.user or not request.user.is_authenticated:
            return False

        # Admin has full access
        if request.user.groups.filter(name='Admin').exists():
            return True

        # Analyst and other authenticated users have no access to events
        return False

    def has_object_permission(self, request, view, obj):
        """Check if user has permission for the specific object"""
        # Same logic as has_permission for consistency
        return self.has_permission(request, view)
