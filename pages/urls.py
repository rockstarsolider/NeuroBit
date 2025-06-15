from django.urls import path

from . import views


urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    
    path('courses/', views.CoursesView.as_view(), name='courses'),

    path('backend/', views.BackendCoursView.as_view(), name='backend_course'),
    path('frontend/', views.FrontendCourseView.as_view(), name='frontend_course'),
    path('ai/', views.AICourseView.as_view(), name='ai_course'),
    path('uiux/', views.UIUXCourseView.as_view(), name='uiux_course'),
    path('gamedev/', views.GameDevCourseView.as_view(), name='gamedev_course'),

    # path('apply/', views.apply_view, name='apply'),
    # path('success/', views.success_view, name='apply_success'),
]
