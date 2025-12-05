from django.shortcuts import render
from .models import Notification
from django.views import View


def mark_notifications_as_read(request):
    if request.method == "POST":
        notifications = Notification.objects.filter(user=request.user, is_read=False)
        notifications.update(is_read=True)
        return render(request, 'notifications/clear_button.html')
    return render(request, 'notifications/clear_button.html')

class NotificationsView(View):
    def get(self, request):
        notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')[:30]
        return render(request, 'notifications/notifications.html', {'notifications': notifications})