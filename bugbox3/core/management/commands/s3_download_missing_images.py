import csv

from django.conf import settings
from django.core.management.base import BaseCommand

from ...tasks import download_s3_media


class Command(BaseCommand):
    """
    Given a .csv files, download the images recorded as missing.
    This is inteded for the output of model training dataset generation step.
    """

    def handle(self, *args, **options):

        if settings.ON_ECDYSIS_SERVER != 'YES' or not settings.LOCAL_MOUNTED_MEDIA:
            print('Currently this cmd is only supported on Ecdysis01')
            return

        file = '/app/local_files/missing_images.csv'
        local_location = '/pool1/srv/bugbox3/bugbox3/media/'
        local_storage_mount = settings.LOCAL_MOUNTED_MEDIA

        with open(file, newline='') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                local_img_destination = row['image']
                source_obj = local_img_destination.replace(local_location, '')
                destination_path = local_storage_mount + source_obj
                print('Downloading: ' + source_obj)
                download_s3_media(source_obj, destination_path)
