from django.core.validators import RegexValidator


def user_directory_path(instance, filename):
    return f'users/images/user_{instance.first_name}-{instance.last_name}/{filename}'

phone_re = RegexValidator(
    regex=r"^(?:\+?\d{1,3})?[0]?\d{9,14}$",
    message="Enter a valid phone number (e.g. +989336628244 or 09336628244).",
)