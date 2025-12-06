from .models import Notification
from asgiref.sync import sync_to_async, async_to_sync

def unread_notifs(request):
    if request.user.is_authenticated:
        get_notifs_sync = lambda: list(
            Notification.objects.filter(
                user=request.user,
                is_read=False
            ).order_by('-created_at')[:8]
        )
        notifs = async_to_sync(sync_to_async(get_notifs_sync))()
        notif_count = len(notifs)

        return {"unread_notifs": notifs, "notif_count": notif_count}
    return {}