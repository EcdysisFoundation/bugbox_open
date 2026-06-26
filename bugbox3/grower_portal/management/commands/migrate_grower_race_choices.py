from django.core.management.base import BaseCommand

from bugbox3.grower_portal.country_choices import COUNTRY_CODE_TO_NAME
from bugbox3.grower_portal.models import GrowerProfile
from bugbox3.grower_portal.phone import is_empty_phone, try_normalize_phone_number
from bugbox3.grower_portal.race import LEGACY_RACE_MAPPING, NEW_RACE_VALUES, RACE_INDIGENOUS


class Command(BaseCommand):
    help = 'migrate legacy grower race values'

    def add_arguments(self, parser):
        parser.add_argument(
            '--apply',
            action='store_true',
            help='this will save the changes',
        )

    def handle(self, *args, **options):
        apply_changes = options['apply']
        mode = 'APPLY' if apply_changes else 'DRY RUN'
        self.stdout.write(f'{mode}: migrate grower race values\n')

        race_updated = 0
        race_skipped = 0
        race_unmapped = []

        profiles = GrowerProfile.objects.all().order_by('id')
        for profile in profiles:
            if not profile.race:
                race_skipped += 1
                continue

            if profile.race in NEW_RACE_VALUES:
                race_skipped += 1
                continue

            mapping = LEGACY_RACE_MAPPING.get(profile.race)
            if not mapping:
                race_unmapped.append((profile.id, profile.race, profile.user.email))
                continue

            new_race, indigenous_country = mapping
            old_race = profile.race
            self.stdout.write(
                f'  Profile id={profile.id} ({profile.user.email}): '
                f'race {old_race!r} -> {new_race!r}'
                + (f', indigenous_country={indigenous_country!r}' if indigenous_country else '')
            )

            if apply_changes:
                profile.race = new_race
                if new_race == RACE_INDIGENOUS and indigenous_country:
                    profile.race_indigenous_country = indigenous_country
                profile.save(update_fields=['race', 'race_indigenous_country', 'updated_at'])
            race_updated += 1

        phone_cleared = 0
        phone_skipped = 0
        for profile in GrowerProfile.objects.exclude(phone__isnull=True).exclude(phone='').order_by('id'):
            if is_empty_phone(profile.phone):
                continue

            normalized, error = try_normalize_phone_number(profile.phone)
            if error:
                self.stdout.write(
                    f'  Profile id={profile.id} ({profile.user.email}): '
                    f'clear invalid phone {profile.phone!r} ({error})'
                )
                if apply_changes:
                    profile.phone = None
                    profile.save(update_fields=['phone', 'updated_at'])
                phone_cleared += 1
            elif normalized == profile.phone:
                phone_skipped += 1

        self.stdout.write(self.style.SUCCESS('\nSummary'))
        self.stdout.write(f'  Race values updated: {race_updated}')
        self.stdout.write(f'  Race values unchanged/skipped: {race_skipped}')
        self.stdout.write(f'  Race values unmapped: {len(race_unmapped)}')
        self.stdout.write(f'  Invalid phones cleared: {phone_cleared}')
        self.stdout.write(f'  Valid phones unchanged: {phone_skipped}')

        if race_unmapped:
            self.stdout.write('\nUnmapped race values (manual review required):')
            for profile_id, race, email in race_unmapped:
                self.stdout.write(f'  Profile id={profile_id} email={email} race={race!r}')

        if not apply_changes and (race_updated or phone_cleared):
            self.stdout.write('\nRe-run with --apply to save changes.')

        self.stdout.write('\nLegacy mapping reference:')
        for old, (new, country) in LEGACY_RACE_MAPPING.items():
            country_label = COUNTRY_CODE_TO_NAME.get(country, '') if country else ''
            suffix = f' + country {country_label}' if country_label else ''
            self.stdout.write(f'  {old!r} -> {new!r}{suffix}')
