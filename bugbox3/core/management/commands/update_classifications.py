from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Exists, OuterRef

from bugbox3.taxonomy.tasks import id_image


class Command(BaseCommand):

    help = 'Send specimens for reclassification if newer model available.' + \
           'Optional --recs to specify number recs to send.'

    def add_arguments(self, parser):
        parser.add_argument('--recs', type=int, help='Number of recs to send.')

    Specimen = apps.get_model(app_label='samples', model_name='Specimen')
    SpecimenImage = apps.get_model(app_label='samples', model_name='SpecimenImage')
    AiTraining = apps.get_model(app_label='taxonomy', model_name='AiTraining')

    def handle(self, *args, **options):
        if settings.ON_ECDYSIS_SERVER != 'YES':
            print('Currently this cmd is only supported on Ecdysis01')
            return
        recs = options.get('recs')
        if not recs:
            recs = 1000
        # The most recent model is determined by the most recent entry into AiTraining
        current_model_name = self.AiTraining.objects.exclude(model_name='').values_list(
            'model_name', flat=True).last()
        specimens = self.Specimen.objects.annotate(
                has_images=Exists(self.SpecimenImage.objects.filter(
                    specimen=OuterRef('pk'),
                    image_notfound=False))).filter(
                acceptance=0,
                has_images=True
            ).exclude(ai_model_name=current_model_name)[:recs]
        for s in specimens:
            id_image.delay(s.id)
        specimen_count = len(specimens)

        message = 'sent {0} image classifications through Celery excluding ai_model_name {1}. '.format(
            specimen_count, current_model_name)
        print(message)
        return
