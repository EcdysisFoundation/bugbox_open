from django.core.management.base import BaseCommand

from bugbox3.grower_portal.models import GrowerApplication, GrowerProfile
from bugbox3.grower_portal.phone import is_empty_phone, try_normalize_phone_number


class Command(BaseCommand):
    help = 'Normalize grower phone numbers to E.164 format.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--apply',
            action='store_true',
            help='this will save the changes',
        )

    def handle(self, *args, **options):
        apply_changes = options['apply']
        updated = 0
        skipped = 0
        failed = []

        self.stdout.write('Scanning GrowerProfile.phone values...')
        for profile in GrowerProfile.objects.exclude(phone__isnull=True).exclude(phone='').order_by('id'):
            result = self._process_value(
                model_label='GrowerProfile',
                record_id=profile.id,
                field_name='phone',
                current_value=profile.phone,
                apply_changes=apply_changes,
                save_callback=lambda value, p=profile: self._save_profile_phone(p, value),
            )
            if result == 'updated':
                updated += 1
            elif result == 'skipped':
                skipped += 1
            elif result:
                failed.append(result)

        self.stdout.write('Scanning GrowerApplication.grower_phone values...')
        for application in GrowerApplication.objects.exclude(grower_phone='').exclude(
            grower_phone__isnull=True
        ).order_by('id'):
            result = self._process_value(
                model_label='GrowerApplication',
                record_id=application.id,
                field_name='grower_phone',
                current_value=application.grower_phone,
                apply_changes=apply_changes,
                save_callback=lambda value, a=application: self._save_application_phone(a, value),
            )
            if result == 'updated':
                updated += 1
            elif result == 'skipped':
                skipped += 1
            elif result:
                failed.append(result)

        mode = 'APPLIED' if apply_changes else 'DRY RUN'
        self.stdout.write(self.style.SUCCESS(f'\n{mode} complete'))
        self.stdout.write(f'  Updated: {updated}')
        self.stdout.write(f'  Already normalized: {skipped}')
        self.stdout.write(f'  Failed: {len(failed)}')

        if failed:
            self.stdout.write('\nFailed records:')
            for item in failed:
                self.stdout.write(
                    f"  {item['model']} id={item['id']} {item['field']}={item['value']!r} "
                    f"reason={item['reason']}"
                )

        if not apply_changes and updated:
            self.stdout.write('\nRe-run with --apply to save normalized phone numbers.')

    def _process_value(self, model_label, record_id, field_name, current_value, apply_changes, save_callback):
        if is_empty_phone(current_value):
            return 'skipped'

        normalized, error = try_normalize_phone_number(current_value)
        if error:
            return {
                'model': model_label,
                'id': record_id,
                'field': field_name,
                'value': current_value,
                'reason': error,
            }

        if normalized == current_value:
            return 'skipped'

        self.stdout.write(
            f"  {model_label} id={record_id}: {current_value!r} -> {normalized!r}"
        )
        if apply_changes:
            save_callback(normalized)
        return 'updated'

    def _save_profile_phone(self, profile, value):
        profile.phone = value
        profile.save(update_fields=['phone', 'updated_at'])

    def _save_application_phone(self, application, value):
        application.grower_phone = value
        application.save(update_fields=['grower_phone'])
