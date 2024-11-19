from django.apps import apps
from django.core.management.base import BaseCommand
from django.db.models import Exists, OuterRef

from bugbox3.taxonomy.tasks import id_image


class Command(BaseCommand):

    Specimen = apps.get_model(app_label='samples', model_name='Specimen')
    SpecimenImage = apps.get_model(app_label='samples', model_name='SpecimenImage')

    def handle(self, *args, **options):
        images_notfound = self.SpecimenImage.objects.filter(
            image_notfound=True
        )
        print(len(images_notfound))
        """
        specimens = self.Specimen.objects.annotate(
            has_images=Exists(self.SpecimenImage.objects.filter(
                specimen=OuterRef('pk'),
                image_notfound=False))).filter(
            ai_classification__isnull=True,
            acceptance=0,
            has_images=True
        )
        print(len(specimens))
        for s in specimens:
            print(s.date_added)
            print('')
        for s in specimens:
            id_image.delay(s.id)
        """
