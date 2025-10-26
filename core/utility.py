from django.core.validators import RegexValidator
from jdatetime import datetime as jdt


def user_directory_path(instance, filename):
    return f'users/images/user_{instance.first_name}-{instance.last_name}/{filename}'

phone_re = RegexValidator(
    regex=r"^(?:\+?\d{1,3})?[0]?\d{9,14}$",
    message="Enter a valid phone number (e.g. +989336628244 or 09336628244).",
)

_MONTHS = ["farvardin","ordibehesht","khordad","tir","mordad","shahrivar",
           "mehr","aban","azar","dey","bahman","esfand"]

def shamsi_text(dt):
    if not dt: return "-"
    j = jdt.fromgregorian(datetime=dt)
    return f"{j.year}-{_MONTHS[j.month-1]}-{j.day:02d}"

def can_access_rosetta(user):
    # Return True if this user is allowed to access Rosetta.
    return user.is_active and user.is_staff