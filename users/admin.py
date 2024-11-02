# users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


class UserAdmin(BaseUserAdmin):
    model = User
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name',
         'birthday', 'cnie', 'phone', 'bank_account')}),
        ('Permissions', {'fields': ('is_active', 'is_staff',
         'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'first_name', 'last_name',
                       'birthday', 'cnie', 'phone', 'bank_account'),
        }),
    )
    list_display = ('username', 'cnie', 'is_staff')
    search_fields = ('username', 'cnie')
    ordering = ('username',)


admin.site.register(User, UserAdmin)

admin.AdminSite.site_header = 'Manage group Daret'
admin.AdminSite.site_title = 'Manage group Daret'
admin.AdminSite.index_title = 'Welcome to DARET Portail'
admin.site.site_url = "http://127.0.0.1:8000/api/v1/auth/login"
