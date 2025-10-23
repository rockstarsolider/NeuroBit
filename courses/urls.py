from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.LearnerDashboardView.as_view(), name='learner-dashboard'),
]
