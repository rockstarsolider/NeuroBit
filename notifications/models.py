from django.conf import settings
from django.db import models
from django.utils import timezone

class Event(models.TextChoices):
    OTHER = 'other', 'Other'

    NEW_EVALUATION = 'new_evaluation', 'New mentor evaluation added'
    NEW_SUBMISSION = 'new_submission', 'Task submission created'
    DEADLINE_APPROACHING = 'deadline_approaching', 'Deadline approaching'
    EXTENSION_REQUESTED = 'extension_requested', 'Extension requested'
    GROUP_SESSION_RESCHEDULED = 'group_session_rescheduled', 'Group session rescheduled'
    MARKED_ABSENT = 'marked_absent', 'Learner marked absent'
    MENTOR_ASSIGNED = 'mentor_assigned', 'Mentor assigned to a learner'
    SUBSCRIPTION_PURCHASED = 'subscription_purchased', 'Subscription purchased'
    SUBSCRIPTION_EXPIRING = 'subscription_expiring', 'Subscription near expiry'
    SUBSCRIPTION_EXPIRED = 'subscription_expired', 'Subscription expired'
    SUBSCRIPTION_FROZEN = 'subscription_frozen', 'Subscription frozen'


class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    title = models.CharField(max_length=255, blank=True)
    message = models.TextField()
    send_email = models.BooleanField(default=False)
    send_sms = models.BooleanField(default=False)
    send_internal = models.BooleanField(default=False)
    event = models.CharField(max_length=50, choices=Event.choices, default=Event.OTHER)
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