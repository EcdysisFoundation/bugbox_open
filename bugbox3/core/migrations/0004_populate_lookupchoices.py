from django.db import migrations


def create_entries(apps, schema_editor):

    LookupChoices = apps.get_model('core', 'LookupChoices')

    TAGS = (
        'adult',
        'alate',
        'apterous',
        'Bobbie',
        'brachypterous',
        'broken',
        'Cassie',
        'Cat Wagner',
        'commensal',
        'egg',
        'Erik',
        'female',
        'Gabe',
        'gravid',
        'juvenile',
        'Kelton review',
        'larva',
        'macropterous',
        'male',
        'Mia',
        'multiple specimens',
        'mummy',
        'nymph',
        'Olivia',
        'parasite',
        'parasitized (dryinid)',
        'parasitized (mermithid)',
        'parasitized (strepsipteran)',
        'pollinator',
        'pupa',
        'queen',
        'teneral',
        'worker',
        'worker (major)'
    )
    TAG_CHOICES = [(v, v) for v in TAGS]

    SITE_HABITAT_TYPES = (
        'alfalfa',
        'almonds',
        'apples',
        'bare',
        'barley',
        'barn',
        'berries',
        'bison',
        'canola',
        'cattle',
        'cherries',
        'citrus',
        'corn',
        'cover crop',
        'dairy',
        'flax',
        'goat',
        'green beans',
        'hay',
        'hazelnut',
        'kernza',
        'lentils',
        'livestock',
        'milo',
        'mixed orchard',
        'n/a',
        'native praire',
        'not in list',
        'oats',
        'pasture',
        'peas',
        'pig',
        'prairie',
        'rangeland',
        'rye',
        'sheep',
        'silvopasture',
        'sorghum',
        'soybeans',
        'sunflower',
        'unknown',
        'vegetable',
        'vineyard',
        'wetland',
        'wheat',
        'winter wheat',
        'woods',
    )
    SITE_HABITAT_TYPE_CHOICES = [(v, v.capitalize()) for v in SITE_HABITAT_TYPES]

    SITE_TREATMENT_TYPES = (
        'conventional',
        'regenerative',
        'transitional',
        'unknown',
        'not in list',
    )

    SITE_TREATMENT_CHOICES = [(v, v.capitalize()) for v in SITE_TREATMENT_TYPES]

    SAMPLE_TYPE_AQUATIC_SWEEP = 'aquatic_sweep'
    SAMPLE_TYPE_BEAT_SHEET_TRAY = 'beat_sheet_tray'
    SAMPLE_TYPE_BEE_BOWL_BLUE = 'bee_bowl_blue'
    SAMPLE_TYPE_BEE_BOWL_COLOR_UNKNOWN = 'bee_bowl_color_unknown'
    SAMPLE_TYPE_BEE_BOWL_WHITE = 'bee_bowl_white'
    SAMPLE_TYPE_BEE_BOWL_YELLOW = 'bee_bowl_yellow'
    SAMPLE_TYPE_BLUE_VANE_TRAP = 'blue_vane_trap'
    SAMPLE_TYPE_DUNG_CORE = 'dung_core'
    SAMPLE_TYPE_HAND_COLLECTION = 'hand_collection'
    SAMPLE_TYPE_MALAISE_TRAP = 'malaise_trap'
    SAMPLE_TYPE_QUADRAT = 'quadrat'
    SAMPLE_TYPE_SOIL_CORE = 'soil_core'
    SAMPLE_TYPE_SOIL_PROBE = 'soil_probe'
    SAMPLE_TYPE_STICKY_TRAP = 'sticky_trap'
    SAMPLE_TYPE_VEGETATION_SWEEP = 'vegetation_sweep'

    SAMPLE_TYPE_CHOICES = (
        (SAMPLE_TYPE_AQUATIC_SWEEP, 'Aquatic sweep'),
        (SAMPLE_TYPE_BEAT_SHEET_TRAY, 'Beat sheet/tray'),
        (SAMPLE_TYPE_BEE_BOWL_BLUE, 'Bee bowl (blue)'),
        (SAMPLE_TYPE_BEE_BOWL_COLOR_UNKNOWN, 'bee bowl (color unknown)'),
        (SAMPLE_TYPE_BEE_BOWL_WHITE, 'Bee bowl (white)'),
        (SAMPLE_TYPE_BEE_BOWL_YELLOW, 'Bee bowl (yellow)'),
        (SAMPLE_TYPE_BLUE_VANE_TRAP, 'Blue vane trap'),
        (SAMPLE_TYPE_DUNG_CORE, 'Dung core'),
        (SAMPLE_TYPE_HAND_COLLECTION, 'Hand collection'),
        (SAMPLE_TYPE_MALAISE_TRAP, 'Malaise trap'),
        (SAMPLE_TYPE_QUADRAT, 'Quadrat'),
        (SAMPLE_TYPE_SOIL_CORE, 'Soil core'),
        (SAMPLE_TYPE_SOIL_PROBE, 'Soil probe'),
        (SAMPLE_TYPE_STICKY_TRAP, 'Sticky trap'),
        (SAMPLE_TYPE_VEGETATION_SWEEP, 'Vegetation sweep'),
    )

    for v in TAG_CHOICES:
        LookupChoices.objects.create(
            field='tags',
            entry=v[0],
            display_txt=v[1]
        )
    for v in SITE_HABITAT_TYPE_CHOICES:
        LookupChoices.objects.create(
            field='habitat_type',
            entry=v[0],
            display_txt=v[1]
        )
    for v in SITE_TREATMENT_CHOICES:
        LookupChoices.objects.create(
            field='treatment',
            entry=v[0],
            display_txt=v[1]
        )
    for v in SAMPLE_TYPE_CHOICES:
        LookupChoices.objects.create(
            field='sample_type',
            entry=v[0],
            display_txt=v[1]
        )
    print('completed creating entries for lookupchoices')


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0003_lookupchoices'),
    ]

    operations = [
        migrations.RunPython(create_entries)
    ]
