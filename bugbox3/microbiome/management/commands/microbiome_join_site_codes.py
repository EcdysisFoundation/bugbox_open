from django.core.management.base import BaseCommand
from django.apps import apps

from bugbox3.microbiome.tasks import join_the_grower_site_code


class Command(BaseCommand):
    """
    Join site codes if they exist.
    """
    def handle(self, *args, **options):
        MicrobiomeTaxa = apps.get_model(app_label='microbiome', model_name='MicrobiomeTaxa')
        ids = MicrobiomeTaxa.objects.values_list('id', flat=True)
        for i in ids:
            join_the_grower_site_code(i)
