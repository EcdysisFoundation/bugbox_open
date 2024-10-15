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

    def handle(self, *args, **options):

        specimens = self.Specimen.objects.values('classification_id').annotate(
                count_class = Count('classification_id')
        ).filter(
                count_class__gt = 104
        ).order_by(
                'classification_id'
        )[:2]


        print(specimens)
        class_id = [item.get('classification_id') for item in specimens]
        print(class_id)
       #  selected = self.Specimen.objects.filter(classification_id__in = class_id).filter(
       #  (Q(acceptance = 1) | Q(acceptance = 2))
       #  )
       # # #
       # #  print(selected)
       # #
       #  selected.update(object_det_train = True)
       # #
       #  print(class_id)
        updated_records = self.Specimen.objects.values('object_det_train', 'classification_id').filter(object_det_train=True)

        print(updated_records)
       # print(specimens)
