import json

from django.apps import apps
from django.core.management.base import BaseCommand
from django.core.serializers.json import DjangoJSONEncoder

from bugbox3.samples import constants


class Command(BaseCommand):
    """
    Create .json from for model training.
    Use Orders at the labels.
    Check that db indicates image has been downloaded.
    """

    SpecimenImage = apps.get_model(app_label='samples', model_name='SpecimenImage')

    def handle(self, *args, **options):
        out_path = 'local_files/obj_det_selections.json'

        q = self.SpecimenImage.objects.filter(
            specimen__classification_id__isnull=False,
            downloaded_image=True,
            object_det_updated_at__isnull=False).exclude(
                specimen__acceptance=constants.ACCEPTANCE_PENDING)

        orders = q.distinct(
                'specimen__classification__gbif_order').order_by(
                    'specimen__classification__gbif_order').values_list(
                    'specimen__classification__gbif_order', flat=True)
        fields = [
            'id',
            'specimen_id',
            constants.SPECIMEN_IMAGE_IMAGE_THUMBNAIL_LARGE,
            'specimen__classification__gbif_canonical_name',
            'specimen__classification__gbif_order',
            constants.SPECIMEN_IMAGE_OBJECT_DET_LABEL
        ]

        q = q.values(*fields)
        serialized_data = json.dumps(list(q), cls=DjangoJSONEncoder)

        # Parse the serialized data to ensure proper JSON formatting
        data = json.loads(serialized_data)

        with open(out_path, 'w') as f:
            json.dump(data, f, indent=2)

        print('Completed export with orders: {0}'.format(orders))
