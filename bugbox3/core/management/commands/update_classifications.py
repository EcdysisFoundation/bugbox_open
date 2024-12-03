from django.apps import apps
from django.core.management.base import BaseCommand
from django.db.models import Min

from bugbox3.taxonomy.tasks import id_image


class Command(BaseCommand):

    Specimen = apps.get_model(app_label='samples', model_name='Specimen')

    def handle(self, *args, **options):
        # set max_ai_version_db_id manually as the database ID
        # of the most recent deployed model we want to update to
        max_ai_version_db_id = 21
        # get the min_ai_version_db_id as the id of lowest ai_version
        min_ai_version_db_id = self.Specimen.objects.aggregate(Min('ai_version_id', default=0))
        min_ai_version_db_id = min_ai_version_db_id['ai_version_id__min']
        record_limit = 10000
        # only update the oldest model version records, limit number of records
        while min_ai_version_db_id < max_ai_version_db_id:
            specimens = self.Specimen.objects.filter(
                ai_version_id__lte=min_ai_version_db_id,
                acceptance=0).exclude(ai_version_id=max_ai_version_db_id)[:record_limit]
            if specimens.count() < record_limit:
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
                max_ai_version_db_id, record_limit)

        print(message)
        return
