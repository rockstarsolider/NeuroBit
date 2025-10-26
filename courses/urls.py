from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.LearnerDashboardView.as_view(), name='learner-dashboard'),
    path('step_list/', views.StepListView.as_view(), name='step-list'),
    path('mentor_feedback_list/', views.MnetorFeedbackListView.as_view(), name='mentor-feedback-list'),
]
