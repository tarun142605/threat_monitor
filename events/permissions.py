from rest_framework import permissions


class EventPermission(permissions.BasePermission):
    """
    Custom permission for events:
    - Admin: full access (create, read, update, delete)
    - Analyst: can create events (POST only)
    - All authenticated users can create events
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Admin has full access
        if request.user.groups.filter(name='Admin').exists():
            return True

        # Analyst and other authenticated users can create events
        if request.method == 'POST':
            return True

        # Other methods require Admin
        return False
