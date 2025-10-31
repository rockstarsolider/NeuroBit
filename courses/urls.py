from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.LearnerDashboardView.as_view(), name='learner-dashboard'),
    path('step_list/', views.StepListView.as_view(), name='step-list'),
    path('task_list/', views.TaskListView.as_view(), name='task-list'),
    path('task_submission/', views.TaskSubmissionView.as_view(), name='task-submission'),
    path('profile_overview/', views.ProfileOverviewView.as_view(), name='profile-overview'),
    path('edit_profile/', views.EditProfileView.as_view(), name='edit-profile'),
    path('learning_path/', views.LearningPathView.as_view(), name='learning-path'),
    path('subscription_plans/', views.SubscriptionPlansView.as_view(), name='subscription-plans'),
    path('step_promise/', views.StepPromiseView.as_view(), name='step-promise'),
    path('task_feedback/', views.TaskFeedbackView.as_view(), name='task-feedback'),

    path('mentor_feedback_list/', views.MnetorFeedbackListView.as_view(), name='mentor-feedback-list'),
    path('mentor_feedback/', views.MnetorFeedbackView.as_view(), name='mentor-feedback'),
    path('attendance_hub/', views.AttendaceHubView.as_view(), name='attendance-hub'),
    path('learners_list/', views.LearnersListView.as_view(), name='learners-list'),
    path('session_list/', views.SessionListView.as_view(), name='session-list'),
    path('group_session_attendance/', views.GroupSessionAttendanceView.as_view(), name='group-session-attendance'),
    path('private_session_attendance/', views.PrivateSessionAttendanceView.as_view(), name='private-session-attendance'),
    path('private_session_manage/', views.PrivateSessionManageView.as_view(), name='private-session-manage'),
    path('learner_attendance_history/', views.LearnerAttendanceHistoryView.as_view(), name='learner-attendance-history'),
    path('group_attendance_history/', views.GroupAttendanceHistoryView.as_view(), name='group-attendance-history'),
]
