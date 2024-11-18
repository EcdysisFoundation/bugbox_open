from django.apps import apps
from django.core.management.base import BaseCommand
from django.db.models import Min

from bugbox3.taxonomy.tasks import id_image


class Command(BaseCommand):

    Specimen = apps.get_model(app_label='samples', model_name='Specimen')

    def handle(self, *args, **options):
        # set max_ai_version_db_id manually as the database ID
        # of the most recent deployed model we want to update to
        max_ai_version_db_id = 18
        # get the min_ai_version_db_id as the id of lowest ai_version
        min_ai_version_db_id = self.Specimen.objects.aggregate(Min('ai_version_id', default=0))
        min_ai_version_db_id = min_ai_version_db_id['ai_version_id__min']
        record_limit = 30000
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
            id_image.delay(s.uuid)
        specimen_count = len(specimens)

        # also run some non-classified images
        non_classified_limit = 3000
        non_classified_specimens = self.Specimen.objects.filter(
                ai_version_id__isnull=True,
                acceptance=0)[:non_classified_limit]
        for s in non_classified_specimens:
            id_image.delay(s.uuid)

        message = 'sent {0} image classifications through Celery up to model db id {1}. '.format(
            specimen_count, min_ai_version_db_id)
        message += 'Process limited by db id {0} and {1} records'.format(
                max_ai_version_db_id, record_limit)

        if non_classified_specimens:
            len_non = str(len(non_classified_specimens))
            message += ' Sent additional {0} specimens without an AI version id, limited by {1}'.format(
                len_non, non_classified_limit)

        print(message)
        return
