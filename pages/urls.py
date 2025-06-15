from django.urls import path

from . import views


urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    
    path('courses/', views.CoursesView.as_view(), name='courses'),
    path('backend/', views.BackendCoursView.as_view(), name='backend_course'),
    
    # path('apply/', views.apply_view, name='apply'),
    # path('success/', views.success_view, name='apply_success'),
]
