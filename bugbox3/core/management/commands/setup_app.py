from django.core.management.base import BaseCommand

from bugbox3.core.permissions_utils import create_app_groups


class Command(BaseCommand):

    def handle(self, *args, **options):
        v = create_app_groups()
        print(v)
