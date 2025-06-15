from django.urls import path

from . import views


urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('apply/', views.apply_view, name='apply'),
    path('success/', views.success_view, name='apply_success'),
]
