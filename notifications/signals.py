from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification


@receiver(post_save, sender=Notification)
def notification_created(sender, instance, created, **kwargs):
    if created and instance.send_internal:
        channel_layer = get_channel_layer()
        group_name = f'notifications_user_{instance.user.id}'
        event = {
            "type": "notification_created",
            "text": instance.title
        }
        async_to_sync(channel_layer.group_send)(group_name, event)