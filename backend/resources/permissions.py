from rest_framework import permissions

class IsDoctorOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow doctors or admins to create content.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        try:
            return request.user.profile.role in ['doctor', 'admin']
        except AttributeError:
            return False
