from datetime import datetime
from django.db import transaction
from django.db.models import Q, Subquery, OuterRef
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

    def handle(self, *args, **options):
        ''' 
        self.Specimen.objects.update(
        object_det_train = Subquery(
                self.Specimen.objects.values('object_det_train').filter(
                        ( Q(acceptance = 1) | Q(acceptance = 2))
                ).annotate(
                        count_class = Count('classification_id')
                ).order_by(
                        'classification_id'
                ).filter(
                        count_class__gt = 104
                )[:5]
                )  
        )
        '''
        specimens = self.Specimen.objects.values('object_det_train').filter(
        (Q(acceptance = 1) | Q(acceptance = 2))
        ).annotate(
                count_class = Count('classification_id')
        ).order_by(
                'classification_id'
        ).filter(
                count_class__gt = 104
        )[:5]
        print(specimens)
	
