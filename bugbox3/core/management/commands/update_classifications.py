from django.apps import apps
from django.core.management.base import BaseCommand
from django.db.models import Max, Min

from bugbox3.taxonomy.tasks import id_image


class Command(BaseCommand):

    help = 'Send specimens for reclassification up to ai_version limit.' + \
           'Optional --recs to specify number recs to send.'

    def add_arguments(self, parser):
        parser.add_argument('--recs', type=int, help='Number of recs to send.')
        parser.add_argument('--db_id', type=int, help='ai_version_id limit.')

    Specimen = apps.get_model(app_label='samples', model_name='Specimen')

    def handle(self, *args, **options):
        recs = options.get('recs')
        db_id = options.get('db_id')
        # set max_ai_version_db_id manually as the database ID
        # of the most recent deployed model we want to update to
        if not db_id:
            db_id = self.Specimen.objects.aggregate(Max('ai_version_id', default=0))
        # get the min_ai_version_db_id as the id of lowest ai_version
        min_ai_version_db_id = self.Specimen.objects.aggregate(Min('ai_version_id', default=0))
        min_ai_version_db_id = min_ai_version_db_id['ai_version_id__min']
        if not recs:
            recs = 1000
        # only update the oldest model version records, limit number of records
        while min_ai_version_db_id < db_id:
            specimens = self.Specimen.objects.filter(
                ai_version_id__lte=min_ai_version_db_id,
                acceptance=0).exclude(ai_version_id=db_id)[:recs]
            if specimens.count() < recs:
                # filter to get more from next model version
                min_ai_version_db_id += 1
            else:
                break
        for s in specimens:
            id_image.delay(s.id)
        specimen_count = len(specimens)

        message = 'sent {0} image classifications through Celery up to model db id {1}. '.format(
            specimen_count, min_ai_version_db_id)
        message += 'Process limited by db id {0} and {1} records'.format(
                db_id, recs)
        print(message)
        return
