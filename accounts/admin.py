"""
Sahaflar Platformu — Accounts Admin
Custom admin configuration for User model.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model

User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'is_verified', 'is_active', 'date_joined']
    list_filter = ['role', 'is_verified', 'is_active', 'is_staff', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'organization']
    ordering = ['-date_joined']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Platform Bilgileri', {
            'fields': ('role', 'phone_number', 'organization', 'location', 'bio', 'avatar', 'is_verified', 'last_activity'),
        }),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Platform Bilgileri', {
            'fields': ('role', 'email', 'first_name', 'last_name'),
        }),
    )
