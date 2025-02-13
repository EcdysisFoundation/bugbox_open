import os

from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand

from ....samples import constants
from ...tasks import download_s3_media


class Command(BaseCommand):
    """
    Download certain images to the Ecdysis01 server from AWS S3.
    """

    SpecimenImage = apps.get_model(app_label='samples', model_name='SpecimenImage')

    # indicates which orgs to download data from
    downaload_data_orgs = [(1, 'Ecdysis Foundation'), ]

    local_storage = 'bugbox3/media/'

    image_files = (constants.SPECIMEN_IMAGE_IMAGE,
                   constants.SPECIMEN_IMAGE_IMAGE_THUMBNAIL,
                   constants.SPECIMEN_IMAGE_IMAGE_THUMBNAIL_MEDIUM,
                   constants.SPECIMEN_IMAGE_IMAGE_THUMBNAIL_LARGE)

    def handle(self, *args, **options):

        if settings.ON_ECDYSIS_SERVER != 'YES':
            print('Currently this cmd is only supported on Ecdysis01')
            return

        org_ids = [v[0] for v in self.downaload_data_orgs]
        org_names = [v[1] for v in self.downaload_data_orgs]

        specimen_images = self.SpecimenImage.objects.filter(
            specimen__sample__site_visit__site__experiment__organization_id__in=org_ids,
            specimen__sample__site_visit__site__experiment__organization__name__in=org_names,
            downloaded_image=False,
            specimen__sample_id=26296  # Remove after testing, limits to a single sample
            )

        # inventory specimen_images to see which have already been downloaded.
        for s in specimen_images:
            # only check full size image for now, but download all sizes
            local_path = self.local_storage + s.image.name
            if os.path.isfile(local_path):
                print('this image is here')
                # image already downloaded, so set to true and dont download
                s.downloaded_image = True
                s.save()
            else:
                # download the images.
                for i in self.image_files:
                    image = getattr(s, i)
                    download_s3_media(image.name, self.local_storage + image.name)
