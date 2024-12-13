import json

from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand

# from datetime import datetime


class Command(BaseCommand):
    """
    Select relevant fields in the tables and create .csv from them for model training.
    """
    Specimen = apps.get_model(app_label='samples', model_name='Specimen')
    AiTraining = apps.get_model('taxonomy', 'AiTraining')
    Morphospecies = apps.get_model('taxonomy', 'Morphospecies')

    def handle(self, *args, **options):
        if not settings.ON_ECDYSIS_SERVER == 'YES':
            print('Currently this cmd is only supported on Ecdysis01')
            return

        json_path = 'local_files/training_stats.json'

        with open(json_path, 'r') as file:
            json_data = json.load(file)
            version = json_data['version']
            if not version:
                print('WARNING: there was no version in the file')
                return
            print('Processing training_stats for model_name {0}'.format(version))
            v = self.AiTraining.objects.filter(model_name=version)
            if v:
                message = 'WARNING: {0} records with model_name = {1} already exist, exiting.'.format(
                    len(v), version
                )
                # or make function to delete existing to update
                print(message)
                return
            obs = [self.AiTraining(**d, model_name=version) for d in json_data['data']]
            created = self.AiTraining.objects.bulk_create(
                    obs)
            print(
                'created {0} AiTraining records for model_name {1}'.format(
                    len(created), version
                )
            )
