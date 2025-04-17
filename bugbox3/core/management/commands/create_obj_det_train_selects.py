import json

from django.apps import apps
from django.core import serializers
from django.core.management.base import BaseCommand

from bugbox3.samples.constants import ACCEPTANCE_PENDING


class Command(BaseCommand):
    """
    Create .json from for model training.
    Use Orders at the labels.
    Check that db indicates image has been downloaded.
    """

    Specimen = apps.get_model(app_label='samples', model_name='Specimen')
    SpecimenImage = apps.get_model(app_label='samples', model_name='SpecimenImage')

    def handle(self, *args, **options):
        out_path = 'local_files/obj_det_selections.json'

        q = self.SpecimenImage.objects.filter(
            specimen__classification_id__isnull=False,
            downloaded_image=True,
            object_det_updated_at__isnull=False).exclude(specimen__acceptance=ACCEPTANCE_PENDING)

        orders = q.distinct(
                'specimen__classification__gbif_order').order_by(
                    'specimen__classification__gbif_order').values_list(
                    'specimen__classification__gbif_order', flat=True)

        fields = ['id', 'specimen_id', 'image', 'specimen__classification__gbif_canonical_name',
                  'specimen__classification__gbif_order', 'object_det_label']

        serialized_data = serializers.serialize('json', q, fields=fields)
        # Parse the serialized data to ensure proper JSON formatting
        data = json.loads(serialized_data)

        with open(out_path, 'w') as f:
            json.dump(data, f, indent=2)

        print('Completed export with orders: {0}'.format(orders))
