from django.core.management.base import BaseCommand

from ...tasks import join_grower_site_codes


class Command(BaseCommand):
    """
    Join site codes if they exist.
    """
    def handle(self, *args, **options):
        join_grower_site_codes()
