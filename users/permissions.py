from rest_framework.permissions import BasePermission, SAFE_METHODS

class RecordPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        if not user.is_authenticated:
            return False

        if user.role == 'admin':
            return True

        if user.role == 'analyst':
            return request.method in SAFE_METHODS 

        if user.role == 'viewer':
            return False  

        return False


class DashboardPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and user.role in ['viewer', 'analyst', 'admin']


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and user.role == 'admin'