from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "title", "send_internal", "send_sms", "send_email", "is_read")
    list_filter = ("send_internal", "send_sms", "send_email", "is_read", "created_at")
    search_fields = ("title", "message",  "user__email")