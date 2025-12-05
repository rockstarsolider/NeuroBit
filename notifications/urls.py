from django.urls import path
from . import views

urlpatterns = [
    path('mark_notifs_as_read/', views.mark_notifications_as_read, name='mark_notifs_as_read'),
    path('notifications/', views.NotificationsView.as_view(), name='notifications')
]