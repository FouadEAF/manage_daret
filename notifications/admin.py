from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user_source', 'user_destination',
                    'message', 'created_at', 'is_read')
    list_filter = ('user_destination', 'is_read')
    search_fields = ('message',)
