from django.core.management.base import BaseCommand

from ....samples.exports import (public_all_img_export,
                                 public_reviewed_img_export)


class Command(BaseCommand):

    # this is also defined in set_public_images
    public_data_orgs = [(1, 'Ecdysis Foundation'), ]

    def handle(self, *args, **options):

        for org in self.public_data_orgs:
            print('creating export for organization: {0}'.format(org[1]))
            filename = public_reviewed_img_export(org[0])
            print('created export filename {0}'.format(filename))
            filename_all = public_all_img_export(org[0])
            print('created export filename {0}'.format(filename_all))
        print('Process completed.')
