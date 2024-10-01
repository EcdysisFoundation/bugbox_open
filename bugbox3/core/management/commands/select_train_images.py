from datetime import datetime

from django.apps import apps
from django.core.management.base import BaseCommand
from label_studio_sdk.client import LabelStudio
from django.db.models.aggregates import Count

class Command(BaseCommand):
    """
    Set which images will be selected for labelstudio with the object_det_train field
    """
    Specimen = apps.get_model(app_label='samples', model_name='Specimen')
    SpecimenImage = apps.get_model(app_label='samples', model_name='SpecimenImage')
    Morphospecies = apps.get_model(app_label='taxonomy', model_name='Morphospecies')

    def set_train_bool(self):
       
        specimens = self.Specimen.objects.filter(
            (acceptance == 1 | acceptance == 2)
        ).values_list(
            'classification', 'acceptance'
        ).order_by(
            'classification', 'acceptance'
        ).aggregate(
               total = Count('classification')__gt=104
        )  

        
        print(specimens.values_list)