from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"
    
    def ready(self):
        # Register models defined in core/notify.py (admin + migrations)
        from . import notify  # noqa: F401
