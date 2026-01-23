from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            'migrations',
            nargs='+',
            help='Migration names to mark as applied (e.g., 0034_specimenimage_image_dimensions)',
        )

    def handle(self, *args, **options):
        migrations = options['migrations']

        with connection.cursor() as cursor:
            for migration_name in migrations:
                cursor.execute(
                    "SELECT COUNT(*) FROM django_migrations WHERE app = 'samples' AND name = %s",
                    [migration_name]
                )
                exists = cursor.fetchone()[0] > 0

                if exists:
                    self.stdout.write(
                        self.style.WARNING(f'Migration {migration_name} is already marked as applied.')
                    )
                else:
                    cursor.execute(
                        "INSERT INTO django_migrations (app, name, applied) VALUES ('samples', %s, NOW())",
                        [migration_name]
                    )
                    self.stdout.write(
                        self.style.SUCCESS(f'Marked migration {migration_name} as applied.')
                    )
