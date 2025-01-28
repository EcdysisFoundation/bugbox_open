

import boto3
from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand

from ....samples import constants


class Command(BaseCommand):
    """
    Set the acl to public-read for specific SpecimenImages.
    """

    SpecimenImage = apps.get_model(app_label='samples', model_name='SpecimenImage')
    Specimen = apps.get_model(app_label='samples', model_name='Specimen')

    public_data_orgs = [(1, 'Ecdysis'), ]

    image_files = (constants.SPECIMEN_IMAGE_IMAGE,
                   constants.SPECIMEN_IMAGE_IMAGE_THUMBNAIL,
                   constants.SPECIMEN_IMAGE_IMAGE_THUMBNAIL_MEDIUM,
                   constants.SPECIMEN_IMAGE_IMAGE_THUMBNAIL_LARGE)

    def handle(self, *args, **options):

        #enable when done testing
        #if settings.ON_ECDYSIS_SERVER != 'YES':
        #    print('Currently this cmd is only supported on Ecdysis01')
        #    return
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )


        org_ids = [v[0] for v in self.public_data_orgs]
        org_names = [v[1] for v in self.public_data_orgs]

        specimen_images = self.SpecimenImage.objects.filter(
            specimen__sample__site_visit__site__experiment__organization_id__in=org_ids,
            specimen__sample__site_visit__site__experiment__organization__name__in=org_names,
            public_image=False,
            specimen__sample_id=22991, #temp remove when done testing
            specimen__classification__isnull=False).exclude(
                specimen__acceptance=0
            )

        if not specimen_images:
            print('No images found to make public, exiting...')
            return
        print('publishing records')

        thecount = 0
        theincrement = range(0, 1000, 100000)
        for s in specimen_images:
            for file in self.image_files:
                s3_client.put_object_acl(
                    Bucket=settings.AWS_STORAGE_BUCKET_NAME_MEDIA,
                    Key=str(getattr(s, file)),
                    ACL='public-read'
                )
            s.public_image=True
            s.save()

            thecount += 1
            if thecount in theincrement:
                print('Processed {0} records, continuing....'.join(thecount))
        print('Process completed.')
