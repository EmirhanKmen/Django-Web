from django.contrib import admin
from .models import Notification, ActivityLog, ContactMessage

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'recipient', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['title', 'message', 'recipient__username']

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'description', 'ip_address', 'created_at']
    list_filter = ['action', 'created_at']
    search_fields = ['user__username', 'description']
    readonly_fields = ['user', 'action', 'description', 'ip_address', 'metadata', 'created_at']

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'is_resolved', 'created_at']
    list_filter = ['is_resolved', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
