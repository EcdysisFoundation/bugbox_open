from django.apps import apps
from django.core.management.base import BaseCommand
from bugbox3.core.utils import create_default_lookup_choices


class Command(BaseCommand):
    help = 'Creates default lookup choices given the provided org_id'

    def add_arguments(self, parser):
        parser.add_argument('org_id', type=int, help='Organization ID')

    def handle(self, *args, **options):
        v = create_default_lookup_choices(options['org_id'])
        print(v)
