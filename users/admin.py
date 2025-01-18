from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, CustomerAccount, SellerProfile, Store

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('phone_number', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('phone_number', 'role', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'password1', 'password2', 'is_staff', 'is_active'),
        }),
    )
    search_fields = ('phone_number', 'role')
    ordering = ('phone_number',)

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(CustomerAccount)
admin.site.register(SellerProfile)
admin.site.register(Store)
