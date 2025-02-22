from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == 'admin'

class IsTrader(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == 'trader'

class IsSales(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == 'sales'

class IsCustomer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == 'customer'