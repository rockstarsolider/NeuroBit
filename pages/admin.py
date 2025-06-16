from django.contrib import admin
from unfold.admin import ModelAdmin
from django.utils.translation import gettext_lazy as _

from .templatetags.custom_translation_tags import translate_number
from .templatetags.persian_calendar_convertor import convert_to_persian_calendar, format_persian_datetime
from .models import Application


@admin.register(Application)
class ApplicationAdmin(ModelAdmin):
    list_display  = ('full_name','phone','location','age','created_at_')
    search_fields = ('full_name','phone','location')
    list_filter   = ('created_at',)

    @admin.display(description=_('created_at'))
    def created_at_(self, obj):
        return translate_number(format_persian_datetime(convert_to_persian_calendar(obj.created_at)))