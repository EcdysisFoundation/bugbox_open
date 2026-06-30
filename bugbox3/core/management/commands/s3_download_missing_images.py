import csv

from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand

from ...tasks import download_s3_media


class Command(BaseCommand):
    """
    Given a .csv file, download the images recorded as missing.
    This is inteded for the output of model training dataset generation step.
    """

    PrivateSiteContent = apps.get_model('core', 'PrivateSiteContent')


    def handle(self, *args, **options):

        if settings.ON_ECDYSIS_SERVER != 'YES' or not settings.LOCAL_MOUNTED_MEDIA:
            print('Currently this cmd is only supported on Ecdysis01')
            return

        recent_missing_images = self.PrivateSiteContent.objects.filter(
            title='missing_images.csv',
            file__icontains='missing_images.csv').last()


        local_location = getattr(
            settings,
            'S3_DOWNLOAD_MEDIA_SOURCE_PREFIX',
            settings.LOCAL_MOUNTED_MEDIA,
        )
        local_storage_mount = settings.LOCAL_MOUNTED_MEDIA

        required_headers = ['morphos_name', 'morphos_id', 'specimen_id', 'image']

        with recent_missing_images.file.open('r') as csv_data:
            reader = csv.DictReader(csv_data)
            headers = list(reader.fieldnames)

            if not all(h in headers for h in required_headers):
                raise ValueError(f"MISSING HEADERS! {required_headers} not in {headers}")

            for row in reader:
                local_img_destination = row['image']
                source_obj = local_img_destination.replace(local_location, '')
                destination_path = local_storage_mount + source_obj
                print('Downloading: ' + source_obj)
                download_s3_media(source_obj, destination_path)
