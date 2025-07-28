# core/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


def user_directory_path(instance, filename):
    return f'users/images/user_{instance.first_name}-{instance.last_name}/{filename}'

phone_re = RegexValidator(
    regex=r"^(?:\+?\d{1,3})?[0]?\d{9,14}$",
    message="Enter a valid phone number (e.g. +989336628244 or 09336628244).",
)


class CustomUser(AbstractUser):
    """
    Subclassing AbstractUser keeps all built‑ins:
    username, first_name, last_name, email, password, is_staff, etc.
    We simply add the extra profile fields you listed.
    """
    phone_number = models.CharField(max_length=15, validators=[phone_re], blank=True)
    image        = models.ImageField(upload_to=user_directory_path, null=True, blank=True)
    national_id  = models.CharField(max_length=30, unique=True)
    home_number  = models.CharField(max_length=10, blank=True)
    city         = models.CharField(max_length=64)
    birthdate    = models.DateField(null=True, blank=True)

    GENDER_CHOICES = [
        ("M", "Male"),
        ("F", "Female"),
        ("O", "Other / Prefer not to say"),
    ]
    gender       = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)

    # no need for a custom manager unless you want extra helpers

    def __str__(self):
        return self.username or self.email
