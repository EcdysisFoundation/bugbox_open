import csv

from django.conf import settings
from django.core.management.base import BaseCommand

from ...tasks import download_s3_media


class Command(BaseCommand):
    """
    Given a .csv files, download the images recorded as missing.
    This is inteded for the output of ultralytics dataset generation step.
    """

    def handle(self, *args, **options):

        if settings.ON_ECDYSIS_SERVER != 'YES' or not settings.LOCAL_MOUNTED_MEDIA:
            print('Currently this cmd is only supported on Ecdysis01')
            return

        file = 'local_files/missing_images.csv'
        local_storage = settings.LOCAL_MOUNTED_MEDIA

        with open(file, newline='') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                img = row['image_thumbnail_large']
                print('Downloading: ' + img)
                download_s3_media(img, local_storage + img)
