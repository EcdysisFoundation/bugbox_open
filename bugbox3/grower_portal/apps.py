from django.apps import AppConfig


class GrowerPortalConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bugbox3.grower_portal'
    verbose_name = 'Grower Portal'

    def ready(self):
        """Import admin registrations when app is ready"""
        from .models import admin  # NOQA
