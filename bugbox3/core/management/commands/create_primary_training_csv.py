from django.core.management.base import BaseCommand

from bugbox3.taxonomy.tasks import export_training_selections


class Command(BaseCommand):
    """
    Create .csv of primary organization images for model training.
    Use all images per specimen.
    Place a limit and minimum and maximum on number of images per catagory.
    """

    def handle(self, *args, **options):
        print('Running Celery task export_training_selections')
        result = export_training_selections.delay()
        print(f'Task id: {result.id}')
