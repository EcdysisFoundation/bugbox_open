from decimal import Decimal, InvalidOperation

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import migrations, models

import bugbox3.grower_portal.constants as constants

HECTARES_PER_ACRE = Decimal('0.40468564224')
CM_PER_INCH = Decimal('2.54')
KG_PER_LB = Decimal('0.45359237')


def _parse_numeric(value):
    if value in (None, ''):
        return None
    try:
        return Decimal(str(value).strip())
    except (InvalidOperation, TypeError, ValueError):
        return None


def _acres_to_ha(acres):
    if acres is None:
        return None
    return (acres * HECTARES_PER_ACRE).quantize(Decimal('0.01'))


def _inches_to_cm(inches):
    if inches is None:
        return None
    return (inches * CM_PER_INCH).quantize(Decimal('0.01'))


def _lbs_to_kg(lbs):
    if lbs is None:
        return None
    return (Decimal(lbs) * KG_PER_LB).quantize(Decimal('0.01'))


def convert_to_metric_canonical(apps, schema_editor):
    Field = apps.get_model('grower_portal', 'Field')
    ManagementPractices = apps.get_model('grower_portal', 'ManagementPractices')
    GrazingEventAnimal = apps.get_model('grower_portal', 'GrazingEventAnimal')

    for field in Field.objects.all().iterator():
        updated_fields = []

        if field.acres_sampled is not None:
            field.area_sampled_ha = _acres_to_ha(field.acres_sampled)
            updated_fields.append('area_sampled_ha')

        paddock_acres = _parse_numeric(field.paddock_size)
        if paddock_acres is not None:
            field.paddock_size_ha = _acres_to_ha(paddock_acres)
            updated_fields.append('paddock_size_ha')

        pasture_acres = _parse_numeric(field.pasture_size)
        if pasture_acres is not None and field.paddock_size_ha is None:
            field.paddock_size_ha = _acres_to_ha(pasture_acres)
            if field.paddock_size_entered is None:
                field.paddock_size_entered = pasture_acres
                field.paddock_size_unit = constants.DEFAULT_AREA_UNIT
                updated_fields.extend(['paddock_size_entered', 'paddock_size_unit'])
            updated_fields.append('paddock_size_ha')

        if field.area_sampled_entered is not None:
            pass
        elif field.area_sampled_ha is not None:
            field.area_sampled_entered = field.area_sampled_ha
            field.area_sampled_unit = constants.AREA_UNIT_HECTARES
            updated_fields.extend(['area_sampled_entered', 'area_sampled_unit'])

        if updated_fields:
            field.save(update_fields=list(set(updated_fields)))

    for practices in ManagementPractices.objects.all().iterator():
        depth_inches = _parse_numeric(practices.tillage_depth)
        if depth_inches is not None:
            practices.tillage_depth_cm = _inches_to_cm(depth_inches)
        if practices.tillage_depth_entered is not None:
            practices.save(update_fields=['tillage_depth_cm'])
        elif practices.tillage_depth_cm is not None:
            practices.tillage_depth_entered = practices.tillage_depth_cm
            practices.tillage_depth_unit = constants.DEPTH_UNIT_CM
            practices.save(update_fields=['tillage_depth_cm', 'tillage_depth_entered', 'tillage_depth_unit'])
        elif depth_inches is not None:
            practices.tillage_depth_entered = depth_inches
            practices.tillage_depth_unit = constants.DEFAULT_DEPTH_UNIT
            practices.save(update_fields=['tillage_depth_cm', 'tillage_depth_entered', 'tillage_depth_unit'])

    for animal in GrazingEventAnimal.objects.all().iterator():
        if animal.average_weight_lbs is not None:
            animal.average_weight_kg = _lbs_to_kg(animal.average_weight_lbs)
            if animal.average_weight_entered is None:
                animal.average_weight_entered = animal.average_weight_lbs
                animal.average_weight_unit = constants.DEFAULT_WEIGHT_UNIT
                animal.save(update_fields=[
                    'average_weight_kg',
                    'average_weight_entered',
                    'average_weight_unit',
                ])
            else:
                animal.save(update_fields=['average_weight_kg'])


class Migration(migrations.Migration):

    dependencies = [
        ('grower_portal', '0051_measurement_entered_values'),
    ]

    operations = [
        migrations.RenameField(
            model_name='field',
            old_name='acres_sampled_entered',
            new_name='area_sampled_entered',
        ),
        migrations.RenameField(
            model_name='field',
            old_name='acres_sampled_unit',
            new_name='area_sampled_unit',
        ),
        migrations.AddField(
            model_name='field',
            name='area_sampled_ha',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text='Canonical sampled area in hectares for reporting',
                max_digits=12,
                null=True,
                validators=[
                    MinValueValidator(constants.AREA_SAMPLED_HA_MIN),
                    MaxValueValidator(constants.AREA_SAMPLED_HA_MAX),
                ],
                verbose_name='Area sampled (hectares)',
            ),
        ),
        migrations.AddField(
            model_name='field',
            name='paddock_size_ha',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text='Canonical paddock size in hectares for reporting',
                max_digits=12,
                null=True,
                verbose_name='Paddock size (hectares)',
            ),
        ),
        migrations.AddField(
            model_name='managementpractices',
            name='tillage_depth_cm',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text='Canonical tillage depth in centimeters for reporting',
                max_digits=12,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='grazingeventanimal',
            name='average_weight_kg',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text='Average weight per animal in kg',
                max_digits=12,
                null=True,
                validators=[
                    MinValueValidator(constants.AVERAGE_WEIGHT_KG_MIN),
                    MaxValueValidator(constants.AVERAGE_WEIGHT_KG_MAX),
                ],
            ),
        ),
        migrations.RunPython(convert_to_metric_canonical, migrations.RunPython.noop),
        migrations.RemoveField(model_name='field', name='acres_sampled'),
        migrations.RemoveField(model_name='field', name='paddock_size'),
        migrations.RemoveField(model_name='field', name='pasture_size'),
        migrations.RemoveField(model_name='managementpractices', name='tillage_depth'),
        migrations.RemoveField(model_name='grazingeventanimal', name='average_weight_lbs'),
    ]
