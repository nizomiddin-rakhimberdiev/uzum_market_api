from rest_framework.permissions import BasePermission

class IsSeller(BasePermission):
    """
    Custom permission to grant access only to users with the 'seller' role.
    """

    def has_permission(self, request, view):
        # Foydalanuvchining tizimga kirganini tekshirish
        if not request.user or not request.user.is_authenticated:
            return False

        # Foydalanuvchining roli 'seller' ekanligini tekshirish
        return hasattr(request.user, 'role') and request.user.role == 'seller'
