from django.core.management.base import BaseCommand

from ....samples.exports import public_all_img_export, public_reviewed_img_export
from ....samples.views_public import PUBLIC_DATA_ORGS


class Command(BaseCommand):

    def handle(self, *args, **options):

        for org in PUBLIC_DATA_ORGS:
            print('creating exports for organization: {0}'.format(org[1]))
            print('creating the reviewed export.')
            filename = public_reviewed_img_export(org[0])
            print('created export filename {0}'.format(filename))
            print('creating the all img export.')
            filename_all = public_all_img_export(org[0])
            print('created export filename {0}'.format(filename_all))
        print('Process completed.')
