

import boto3
import csv
from datetime import datetime, timezone
from tempfile import SpooledTemporaryFile
from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.files import File

from ....samples import constants
from ....libs.utilities import get_media_url


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

    temp_max_memory_size = 5 * (2**20)
    export_title = 'public-images'
    filename_extension = 'csv'

    export_values = ['id', 'specimen_id', 'image_thumbnail_large']
    export_values += ['specimen__sample__site_visit__' + v for v in ['visit_date']]
    export_values += ['specimen__sample__site_visit__site__' + v for v in ['country', 'state_region', 'county_region', 'us_state_county_fips']]
    export_values += ['specimen__classification__' + v for v in ['gbif_canonical_name', 'gbif_order', 'gbif_family', 'gbif_genus', 'gbif_species']]

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
            print('No images found to make public')
        else:
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
            s.public_image = True
            s.save()

            thecount += 1
            if thecount in theincrement:
                print('Processed {0} records, continuing....'.join(thecount))

        if specimen_images:
            print('selected images are now public')

        print('creating export file')
        for org in self.public_data_orgs:
            print('creating export for organization: {0}'.format(org[1]))

            # make filename
            now = datetime.now(tz=timezone.utc)
            filename = '__'.join([self.export_title, now.strftime('%Y-%m-%d_%H%M%S')])
            filename = '%s.%s' % (filename, self.filename_extension)

            # query data
            data = self.SpecimenImage.objects.filter(
                specimen__sample__site_visit__site__experiment__organization_id=org[0],
                specimen__sample__site_visit__site__experiment__organization__name=org[1],
                public_image=True).values(*self.export_values)

            with SpooledTemporaryFile(mode='w', newline='', max_size=self.temp_max_memory_size) as tmpfile:
                writer = csv.writer(tmpfile)
                writer.writerow(self.export_values + ['public_url'])
                for i in data:
                    url = settings.MEDIA_URL + i['image_thumbnail_large']
                    writer.writerow([str(i[v]) for v in self.export_values] + [url])
                file_obj = File(tmpfile, name=filename)
                self.Exports.objects.create(
                    organization_id=org[0],
                    title=self.export_title,
                    file=file_obj,
                )

        print('Process completed.')
