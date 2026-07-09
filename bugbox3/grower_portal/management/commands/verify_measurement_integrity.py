from decimal import Decimal

from django.core.management.base import BaseCommand

from bugbox3.grower_portal.constants import DEFAULT_AREA_UNIT, DEFAULT_DEPTH_UNIT, DEFAULT_WEIGHT_UNIT
from bugbox3.grower_portal.measurement_units import (
    canonical_matches_entered,
    to_cm,
    to_days,
    to_hectares,
    to_kg,
)
from bugbox3.grower_portal.models import Field, GrazingEventAnimal, ManagementPractices


class Command(BaseCommand):
    help = 'Verify grower-entered measurements match canonical metric storage.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Recompute canonical values from entered + unit when mismatched.',
        )
        parser.add_argument('--field-id', type=int, help='Limit checks to one Field id.')
        parser.add_argument(
            '--tolerance',
            type=str,
            default='0.02',
            help='Absolute tolerance for decimal canonical comparisons (default: 0.02).',
        )

    def handle(self, *args, **options):
        tolerance = Decimal(options['tolerance'])
        fix = options['fix']
        field_qs = Field.objects.all()
        if options['field_id']:
            field_qs = field_qs.filter(pk=options['field_id'])

        mismatches = []
        fixed = 0

        for field in field_qs.iterator():
            row_mismatches, row_fixed = self._check_field(field, tolerance, fix)
            mismatches.extend(row_mismatches)
            fixed += row_fixed

        practices_qs = ManagementPractices.objects.select_related('application__field')
        if options['field_id']:
            practices_qs = practices_qs.filter(application__field_id=options['field_id'])
        for practices in practices_qs.iterator():
            row_mismatches, row_fixed = self._check_practices(practices, tolerance, fix)
            mismatches.extend(row_mismatches)
            fixed += row_fixed

        animal_qs = GrazingEventAnimal.objects.select_related('grazing_event__application__field')
        if options['field_id']:
            animal_qs = animal_qs.filter(grazing_event__application__field_id=options['field_id'])
        for animal in animal_qs.iterator():
            row_mismatches, row_fixed = self._check_animal(animal, tolerance, fix)
            mismatches.extend(row_mismatches)
            fixed += row_fixed

        if mismatches:
            self.stdout.write(self.style.WARNING(f'Found {len(mismatches)} mismatch(es):'))
            for message in mismatches:
                self.stdout.write(f'  - {message}')
        else:
            self.stdout.write(self.style.SUCCESS('All checked measurements are consistent.'))

        if fix:
            self.stdout.write(self.style.SUCCESS(f'Fixed {fixed} row(s).'))
        elif mismatches:
            self.stdout.write('Re-run with --fix to recompute canonical values from entered data.')

    def _check_field(self, field, tolerance, fix):
        mismatches = []
        fixed = 0
        specs = (
            (
                f'Field {field.pk} area_sampled',
                field.area_sampled_entered,
                field.area_sampled_unit or DEFAULT_AREA_UNIT,
                field.area_sampled_ha,
                'area',
                'area_sampled_ha',
            ),
            (
                f'Field {field.pk} paddock_size',
                field.paddock_size_entered,
                field.paddock_size_unit or DEFAULT_AREA_UNIT,
                field.paddock_size_ha,
                'area',
                'paddock_size_ha',
            ),
        )
        for label, entered, unit, canonical, measurement_type, canonical_attr in specs:
            if entered is None and canonical is None:
                continue
            if canonical_matches_entered(
                entered, unit, canonical, measurement_type=measurement_type, tolerance=tolerance
            ):
                continue
            mismatches.append(
                f'{label}: entered={entered} {unit}, canonical={canonical}'
            )
            if fix and entered is not None:
                setattr(field, canonical_attr, to_hectares(entered, unit))
                field.save(update_fields=[canonical_attr])
                fixed += 1
        return mismatches, fixed

    def _check_practices(self, practices, tolerance, fix):
        mismatches = []
        fixed = 0
        if practices.tillage_depth_entered is None and practices.tillage_depth_cm is None:
            return mismatches, fixed
        if not canonical_matches_entered(
            practices.tillage_depth_entered,
            practices.tillage_depth_unit or DEFAULT_DEPTH_UNIT,
            practices.tillage_depth_cm,
            measurement_type='depth',
            tolerance=tolerance,
        ):
            label = f'ManagementPractices {practices.pk} tillage_depth'
            mismatches.append(
                f'{label}: entered={practices.tillage_depth_entered} '
                f'{practices.tillage_depth_unit}, canonical={practices.tillage_depth_cm}'
            )
            if fix and practices.tillage_depth_entered is not None:
                practices.tillage_depth_cm = to_cm(
                    practices.tillage_depth_entered,
                    practices.tillage_depth_unit or DEFAULT_DEPTH_UNIT,
                )
                practices.save(update_fields=['tillage_depth_cm'])
                fixed += 1
        return mismatches, fixed

    def _check_animal(self, animal, tolerance, fix):
        mismatches = []
        fixed = 0
        weight_specs = (
            (
                f'GrazingEventAnimal {animal.pk} average_weight',
                animal.average_weight_entered,
                animal.average_weight_unit or DEFAULT_WEIGHT_UNIT,
                animal.average_weight_kg,
                'weight',
                'average_weight_kg',
                to_kg,
            ),
        )
        duration_specs = (
            (
                f'GrazingEventAnimal {animal.pk} duration',
                animal.duration_entered,
                animal.duration_unit,
                animal.duration_days,
                'duration',
                'duration_days',
                to_days,
            ),
            (
                f'GrazingEventAnimal {animal.pk} rest_period',
                animal.rest_period_entered,
                animal.rest_period_unit,
                animal.rest_period_days,
                'duration',
                'rest_period_days',
                to_days,
            ),
        )
        for label, entered, unit, canonical, measurement_type, canonical_attr, converter in (
            *weight_specs,
            *duration_specs,
        ):
            if entered is None and canonical is None:
                continue
            if canonical_matches_entered(
                entered, unit, canonical, measurement_type=measurement_type, tolerance=tolerance
            ):
                continue
            mismatches.append(f'{label}: entered={entered} {unit}, canonical={canonical}')
            if fix and entered is not None:
                setattr(animal, canonical_attr, converter(entered, unit))
                animal.save(update_fields=[canonical_attr])
                fixed += 1
        return mismatches, fixed
