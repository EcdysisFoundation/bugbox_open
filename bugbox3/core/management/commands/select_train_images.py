from datetime import datetime

from django.apps import apps
from django.core.management.base import BaseCommand
#from label_studio_sdk.client import LabelStudio
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
            (Q(acceptance = 1) | Q(acceptance = 2))
        ).order_by(
            'classification'
        ).annotate(
               count_class = Count('classification')
        ).filter(
		count_class__gt = 104
	)


        print(specimens.values_list)
