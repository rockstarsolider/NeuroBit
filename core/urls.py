from django.urls import path
from . import views

urlpatterns = [
    path("auth/", views.phone_view, name="phone_view"),
    path("auth/verify/", views.verify_otp, name="verify_otp"),
]
