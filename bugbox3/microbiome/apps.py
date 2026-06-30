from django.apps import AppConfig


class MicrobiomeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bugbox3.microbiome'
    verbose_name = 'Microbiome'

    def ready(self):
        import bugbox3.microbiome.signals  
