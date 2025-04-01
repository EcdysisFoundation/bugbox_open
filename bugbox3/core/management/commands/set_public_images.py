import boto3
import botocore
from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Q

from ....libs.utilities import save_specimen_img_thumbs
from ....samples import constants
from ....samples.exports import public_reviewed_img_export


class Command(BaseCommand):
    """
    Set the acl to public-read for specific SpecimenImages.
    """

    SpecimenImage = apps.get_model(app_label='samples', model_name='SpecimenImage')
    Specimen = apps.get_model(app_label='samples', model_name='Specimen')
    Exports = apps.get_model(app_label='core', model_name='Exports')

    public_data_orgs = [(1, 'Ecdysis Foundation'), ]

    image_files = (constants.SPECIMEN_IMAGE_IMAGE,
                   constants.SPECIMEN_IMAGE_IMAGE_THUMBNAIL,
                   constants.SPECIMEN_IMAGE_IMAGE_THUMBNAIL_MEDIUM,
                   constants.SPECIMEN_IMAGE_IMAGE_THUMBNAIL_LARGE)

    def handle(self, *args, **options):

        if settings.ON_ECDYSIS_SERVER != 'YES':
            print('Currently this cmd is only supported on Ecdysis01')
            return
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )

        org_ids = [v[0] for v in self.public_data_orgs]
        org_names = [v[1] for v in self.public_data_orgs]

        # check for missing thumbnails first, since there should be very few
        imgs_missing_thumbs = self.SpecimenImage.objects.filter(
            Q(image_thumbnail='') | Q(image_thumbnail_medium='') | Q(image_thumbnail_large='')
        )
        for i in imgs_missing_thumbs:
            # check for thumbnails and save them if they dont exist.
            save_specimen_img_thumbs(i)

        specimen_images = self.SpecimenImage.objects.filter(
            specimen__sample__site_visit__site__experiment__organization_id__in=org_ids,
            specimen__sample__site_visit__site__experiment__organization__name__in=org_names,
            public_image=False,
            specimen__classification__isnull=False).exclude(
                specimen__acceptance=0
            )

        if not specimen_images:
            print('No images found to make public')
        else:
            print('publishing records')

        thecount = 0
        theincrement = range(0, 100000, 1000)
        for s in specimen_images:
            for file in self.image_files:
                key = str(getattr(s, file))
                if key:
                    try:
                        s3_client.put_object_acl(
                            Bucket=settings.AWS_STORAGE_BUCKET_NAME_MEDIA,
                            Key=key,
                            ACL='public-read'
                        )
                    except botocore.exceptions.ClientError as error:
                        print(s.id)
                        raise error

            s.public_image = True
            s.save()

            thecount += 1
            if thecount in theincrement:
                print('Processed {0} records, continuing....'.format(thecount))

        if specimen_images:
            print('selected images are now public')

        print('creating export file')
        for org in self.public_data_orgs:
            print('creating export for organization: {0}'.format(org[1]))
            filename = public_reviewed_img_export(org[0])
            print('created export filename {0}'.format(filename))
        print('Process completed.')
