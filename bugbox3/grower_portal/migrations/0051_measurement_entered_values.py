from decimal import Decimal, InvalidOperation

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import migrations, models

import bugbox3.grower_portal.constants as constants


def _parse_numeric(value):
    if value in (None, ''):
        return None
    try:
        return Decimal(str(value).strip())
    except (InvalidOperation, TypeError, ValueError):
        return None


def backfill_entered_measurements(apps, schema_editor):
    Field = apps.get_model('grower_portal', 'Field')
    ManagementPractices = apps.get_model('grower_portal', 'ManagementPractices')
    GrazingEventAnimal = apps.get_model('grower_portal', 'GrazingEventAnimal')

    for field in Field.objects.all().iterator():
        updated = False
        if field.acres_sampled is not None and field.acres_sampled_entered is None:
            field.acres_sampled_entered = field.acres_sampled
            field.acres_sampled_unit = constants.DEFAULT_AREA_UNIT
            updated = True
        paddock = _parse_numeric(field.paddock_size)
        if paddock is not None and field.paddock_size_entered is None:
            field.paddock_size_entered = paddock
            field.paddock_size_unit = constants.DEFAULT_AREA_UNIT
            updated = True
        if updated:
            field.save(update_fields=[
                'acres_sampled_entered',
                'acres_sampled_unit',
                'paddock_size_entered',
                'paddock_size_unit',
            ])

    for practices in ManagementPractices.objects.all().iterator():
        depth = _parse_numeric(practices.tillage_depth)
        if depth is not None and practices.tillage_depth_entered is None:
            practices.tillage_depth_entered = depth
            practices.tillage_depth_unit = constants.DEFAULT_DEPTH_UNIT
            practices.save(update_fields=['tillage_depth_entered', 'tillage_depth_unit'])

    for animal in GrazingEventAnimal.objects.all().iterator():
        updated = False
        if animal.average_weight_lbs is not None and animal.average_weight_entered is None:
            animal.average_weight_entered = animal.average_weight_lbs
            updated = True
        if animal.duration_days is not None and animal.duration_entered is None:
            animal.duration_entered = animal.duration_days
            updated = True
        if animal.rest_period_days is not None and animal.rest_period_entered is None:
            animal.rest_period_entered = animal.rest_period_days
            updated = True
        if updated:
            animal.save(update_fields=[
                'average_weight_entered',
                'duration_entered',
                'rest_period_entered',
            ])


class Migration(migrations.Migration):

    dependencies = [
        ('grower_portal', '0050_grazingeventanimal_measurement_units'),
    ]

    operations = [
        migrations.AddField(
            model_name='field',
            name='acres_sampled_entered',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text='Sampled area as entered by the grower',
                max_digits=12,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='field',
            name='acres_sampled_unit',
            field=models.CharField(
                blank=True,
                choices=constants.AREA_UNIT_CHOICES,
                default=constants.DEFAULT_AREA_UNIT,
                help_text='Unit used when entering sampled area',
                max_length=10,
            ),
        ),
        migrations.AddField(
            model_name='field',
            name='paddock_size_entered',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text='Paddock size as entered by the grower',
                max_digits=12,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='field',
            name='paddock_size_unit',
            field=models.CharField(
                blank=True,
                choices=constants.AREA_UNIT_CHOICES,
                default=constants.DEFAULT_AREA_UNIT,
                help_text='Unit used when entering paddock size',
                max_length=10,
            ),
        ),
        migrations.AddField(
            model_name='managementpractices',
            name='tillage_depth_entered',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text='Tillage depth as entered by the grower',
                max_digits=12,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='managementpractices',
            name='tillage_depth_unit',
            field=models.CharField(
                blank=True,
                choices=constants.DEPTH_UNIT_CHOICES,
                default=constants.DEFAULT_DEPTH_UNIT,
                help_text='Unit used when entering tillage depth',
                max_length=10,
            ),
        ),
        migrations.AddField(
            model_name='grazingeventanimal',
            name='average_weight_entered',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text='Average weight as entered by the grower',
                max_digits=12,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='grazingeventanimal',
            name='duration_entered',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text='Grazing duration as entered by the grower',
                max_digits=12,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='grazingeventanimal',
            name='rest_period_entered',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text='Rest period as entered by the grower',
                max_digits=12,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name='field',
            name='acres_sampled',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text='Canonical sampled area in acres for reporting',
                max_digits=8,
                null=True,
                validators=[
                    MinValueValidator(Decimal('0.1')),
                    MaxValueValidator(Decimal('10000')),
                ],
                verbose_name='Acres sampled',
            ),
        ),
        migrations.AlterField(
            model_name='field',
            name='paddock_size',
            field=models.CharField(
                blank=True,
                help_text='Canonical paddock size in acres for reporting',
                max_length=constants.PADDOCK_SIZE_MAX_LENGTH,
                verbose_name='Paddock size (acres)',
            ),
        ),
        migrations.AlterField(
            model_name='managementpractices',
            name='tillage_depth',
            field=models.CharField(
                blank=True,
                help_text='Canonical tillage depth in inches for reporting',
                max_length=constants.TILLAGE_DEPTH_MAX_LENGTH,
            ),
        ),
        migrations.RunPython(backfill_entered_measurements, migrations.RunPython.noop),
    ]
