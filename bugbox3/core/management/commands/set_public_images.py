import boto3
import botocore
from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Q

from ....libs.utilities import save_specimen_img_thumbs
from ....samples import constants
from ....samples.views_public import PUBLIC_DATA_ORGS


class Command(BaseCommand):
    """
    Set the acl to public-read for specific SpecimenImages.
    """

    SpecimenImage = apps.get_model(app_label='samples', model_name='SpecimenImage')

    image_files = (constants.SPECIMEN_IMAGE_IMAGE,
                   constants.SPECIMEN_IMAGE_IMAGE_THUMBNAIL,
                   constants.SPECIMEN_IMAGE_IMAGE_THUMBNAIL_MEDIUM,
                   constants.SPECIMEN_IMAGE_IMAGE_THUMBNAIL_LARGE)

    s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )

    def make_public_acl(self, s, file):
        key = str(getattr(s, file))
        if key:
            try:
                self.s3_client.put_object_acl(
                    Bucket=settings.AWS_STORAGE_BUCKET_NAME_MEDIA,
                    Key=key,
                    ACL='public-read'
                )
            except botocore.exceptions.ClientError as error:
                print(s.id)
                raise error

    def handle(self, *args, **options):

        if settings.ON_ECDYSIS_SERVER != 'YES':
            print('Currently this cmd is only supported on Ecdysis01')
            return

        org_ids = [v[0] for v in PUBLIC_DATA_ORGS]
        org_names = [v[1] for v in PUBLIC_DATA_ORGS]

        # check for missing thumbnails first, since there should be very few
        imgs_missing_thumbs = self.SpecimenImage.objects.filter(
            Q(image_thumbnail='') | Q(image_thumbnail_medium='') | Q(image_thumbnail_large='')
        )
        if imgs_missing_thumbs:
            print('{0} images dont have thumbnails'.format(len(imgs_missing_thumbs)))
            print('skipping fixing these for now')
            # Note: disabled creating new thumbnails till figure out why some wont regenerate.
            # for i in imgs_missing_thumbs:
            #    # check for thumbnails and save them if they dont exist.
            #    save_specimen_img_thumbs(i)

        # Process reviewed images
        specimen_images = self.SpecimenImage.objects.filter(
            specimen__sample__site_visit__site__experiment__organization_id__in=org_ids,
            specimen__sample__site_visit__site__experiment__organization__name__in=org_names,
            public_image=False,
            specimen__classification__isnull=False).exclude(
                specimen__acceptance=0
            )

        if not specimen_images:
            print('No reviewed images found to make public.')
        else:
            print('Publishing newly reviewed images.')

        thecount = 0
        theincrement = range(0, 100000, 1000)
        for s in specimen_images:
            for file in self.image_files:
                self.make_public_acl(s, file)
            s.public_image = True
            s.save()

            thecount += 1
            if thecount in theincrement:
                print('Processed {0} reviewed records, continuing....'.format(thecount))

        if specimen_images:
            print('selected reviewed images are now public')

        # Process non-reviwed images, with a limit
        image_limit = 100000
        specimen_images = self.SpecimenImage.objects.filter(
            specimen__sample__site_visit__site__experiment__organization_id__in=org_ids,
            specimen__sample__site_visit__site__experiment__organization__name__in=org_names,
            public_image=False,
            specimen__acceptance=0,
            specimen__ai_classification__isnull=False)[:image_limit]

        if not specimen_images:
            print('No other images found to make public.')
        else:
            print('Publishing {0} images. Limit set at {1}'.format(len(specimen_images), image_limit))

        thecount = 0
        for s in specimen_images:
            for file in self.image_files:
                self.make_public_acl(s, file)
            s.public_image = True
            s.save()

            thecount += 1
            if thecount in theincrement:
                print('Processed {0} other images, continuing....'.format(thecount))

        if specimen_images:
            print('selected other images are now public')

        print('Process completed.')
