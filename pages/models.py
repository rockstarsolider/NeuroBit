from django.db import models
from django.core.validators import FileExtensionValidator


def directory_path(instance, filename):
    return f'{instance.id}/{instance.fullname}/{filename}'


class Application(models.Model):
    full_name = models.CharField("Full name", max_length=255)
    phone = models.CharField("Phone number", max_length=30, blank=True)
    location = models.CharField("Location", max_length=255, blank=True)
    age = models.PositiveIntegerField("Age")
    sopfile = models.FileField(
        upload_to=directory_path, 
        validators=[FileExtensionValidator(['pdf'])],
        blank=True, null=True,
        verbose_name="SOP file", 
        )
    
    created_at = models.DateTimeField(auto_now_add=True)
    datetime_edited = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name

