import requests
from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand

from bugbox3.taxonomy.tasks import obj_det_image


class Command(BaseCommand):

    SpecimenImage = apps.get_model(app_label='samples', model_name='SpecimenImage')

    def handle(self, *args, **options):
        if settings.AI_INFERENCE_URL:

            # get the current model version
            response = requests.get(settings.AI_INFERENCE_URL + 'yolo', timeout=25)
            print(response)
            try:
                response.raise_for_status()
                response = response.json()
            except Exception as e:
                print(str(e))
                return
            model_version = response['version']
            if not model_version:
                print('Yolo model is disabled, exiting..')
                return
            # dont overwrite human verified where object_det_id present
            specimens = self.SpecimenImage.objects.filter(
                object_det_id__isnull=True).exclude(
                    object_det_model_version=model_version
            ).exclude(specimen__acceptance=0).exclude(
                image_thumbnail_large=''
            )[:1000]
            for s in specimens:
                obj_det_image.delay(s.id)
        else:
            print(
                'AI_INFERENCE_URL is unavailable, classify_obj_det_images command not run.'
            )
