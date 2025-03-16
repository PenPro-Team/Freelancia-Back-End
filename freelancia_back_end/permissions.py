from rest_framework import permissions

from freelancia_back_end.models import User

from rest_framework import permissions
from freelancia_back_end.models import User

from rest_framework import permissions
from freelancia_back_end.models import User

class IsOwnerOrAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow:
    - Anyone to read the object (GET).
    - The owner to edit the object (PUT, PATCH).
    - The owner or admin to delete the object (DELETE).
    """

    def __init__(self, owner_field_name='user'):
        self.owner_field_name = owner_field_name

    def has_permission(self, request, view):
        if request.method == 'GET':
            return True
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method == 'GET':
            return True

        owner = getattr(obj, self.owner_field_name)

        if request.method in ['PUT', 'PATCH']:
            return request.user == owner

        if request.method == 'DELETE':
            return request.user == owner or request.user.role == User.RoleChoices.admin

        return False