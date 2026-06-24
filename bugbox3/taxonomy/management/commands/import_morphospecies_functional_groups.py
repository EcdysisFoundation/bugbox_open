from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from bugbox3.taxonomy.functional_group_csv import read_functional_groups_csv, row_to_trait_weights
from bugbox3.taxonomy.functional_groups import set_trait_weights_for_morphospecies
from bugbox3.taxonomy.models import Morphospecies


class Command(BaseCommand):
    help = 'Import morphospecies functional-group weights from Kelton CSV'

    def add_arguments(self, parser):
        parser.add_argument('csv_path', type=str, help='Path to morphospecies_functional_groups.csv')
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Report changes without writing to the database.',
        )

    def handle(self, *args, **options):
        path = Path(options['csv_path'])
        dry_run = options['dry_run']
        if not path.exists():
            raise CommandError(f'File not found: {path}')

        rows = read_functional_groups_csv(path)
        morphos_by_id = {m.id: m for m in Morphospecies.objects.all()}
        morphos_by_name = {m.name: m for m in Morphospecies.objects.all()}

        imported = 0
        skipped_no_morpho = []
        skipped_no_traits = 0

        def import_rows():
            nonlocal imported, skipped_no_traits
            for row in rows:
                morpho = None
                row_id = row.get('id', '').strip()
                if row_id:
                    try:
                        morpho = morphos_by_id.get(int(row_id))
                    except ValueError:
                        morpho = None
                if morpho is None and row.get('name'):
                    morpho = morphos_by_name.get(row['name'].strip())
                if morpho is None:
                    skipped_no_morpho.append(row_id or row.get('name', ''))
                    continue

                weights = row_to_trait_weights(row)
                if not weights:
                    skipped_no_traits += 1
                    continue

                set_trait_weights_for_morphospecies(morpho, weights, validate=True)
                imported += 1

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN'))
            for row in rows:
                row_id = row.get('id', '').strip()
                morpho = None
                if row_id:
                    try:
                        morpho = morphos_by_id.get(int(row_id))
                    except ValueError:
                        morpho = None
                if morpho is None and row.get('name'):
                    morpho = morphos_by_name.get(row['name'].strip())
                if morpho is None:
                    skipped_no_morpho.append(row_id or row.get('name', ''))
                    continue
                if not row_to_trait_weights(row):
                    skipped_no_traits += 1
                    continue
                imported += 1
        else:
            with transaction.atomic():
                import_rows()

        self.stdout.write(self.style.SUCCESS(f'Imported: {imported}'))
        self.stdout.write(f'Skipped (no morphospecies): {len(skipped_no_morpho)}')
        self.stdout.write(f'Skipped (no trait weights): {skipped_no_traits}')
        if skipped_no_morpho[:10]:
            self.stdout.write('Examples missing morphospecies: ' + ', '.join(skipped_no_morpho[:10]))
