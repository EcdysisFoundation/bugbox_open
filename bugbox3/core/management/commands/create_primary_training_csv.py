from django.core.management.base import BaseCommand

from bugbox3.taxonomy.tasks import export_training_selections


class Command(BaseCommand):
    """
    Create .csv of primary organization images for model training.
    Use all images per specimen.
    Place a limit and minimum and maximum on number of images per catagory.
    """

    def add_arguments(self, parser):
        parser.add_argument(
            '--min-imgs',
            type=int,
            default=20
        )
        parser.add_argument(
            '--max-imgs',
            type=int,
            default=200
        )

    def handle(self, *args, **options):
        min_imgs = options['min_imgs']
        max_imgs = options['max_imgs']
        print('Running Celery task export_training_selections')
        result = export_training_selections.delay(min_imgs, max_imgs)
        print(f'Task id: {result.id}')
