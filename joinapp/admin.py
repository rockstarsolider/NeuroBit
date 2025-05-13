from django.contrib import admin
from .models import Application

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display  = ('full_name','phone','location','age','created_at')
    search_fields = ('full_name','phone','location')
    list_filter   = ('created_at',)
