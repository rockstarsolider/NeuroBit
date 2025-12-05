from django.conf import settings
from django.db import models
from django.utils import timezone

class Type(models.TextChoices):
        INTERNAL = "internal", "Internal"
        EMAIL = "email", "Email"
        SMS = "sms", "SMS"


class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    type = models.CharField(max_length=12, choices=Type.choices, default=Type.INTERNAL)
    title = models.CharField(max_length=255)
    message = models.TextField(blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=("user", "is_read", "created_at")),
            models.Index(fields=("user", "created_at")),
        ]

    def mark_read(self):
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=["is_read"])