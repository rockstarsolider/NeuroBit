# core/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models
from .utility import phone_re, user_directory_path


class GenderChoices(models.TextChoices):
    MALE = "M", "Male"
    FEMALE = "F", "Female"
    OTHER = "O", "Other / Prefer not to say"

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
    gender = models.CharField(max_length=1, choices=GenderChoices, default=GenderChoices.MALE, blank=True)

    # no need for a custom manager unless you want extra helpers

    def __str__(self):
        return self.username or self.email
