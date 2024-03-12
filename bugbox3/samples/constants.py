from itertools import chain

from django.db.models.fields import BLANK_CHOICE_DASH

# Fields

FIELD_UUID = 'uuid'
FIELD_NAME = 'name'
FIELD_ABBREVIATION = 'abbreviation'
FIELD_FROM_YEAR = 'from_year'
FIELD_TO_YEAR = 'to_year'
FIELD_LEADER = 'leader'
FIELD_NO_SITES = 'no_sites'
FIELD_DATE_PER_SITE = 'date_per_site'
FIELD_COMPLETED = 'completed'
FIELD_SUMMARY = 'summary'

FIELD_SAMPLE_PLAN_ID = 'id'
FIELD_SAMPLE_PLAN_SAMPLE_TYPE = 'sample_type'
FIELD_SAMPLE_PLAN_NO_PER_DATE = 'no_per_date'
FIELD_SAMPLE_PLAN_NAME_NO_PER_TYPE = 'name_no_per_type'

FIELD_SITE_SITE_NAME = 'site_name'
FIELD_SITE_HABITAT_TYPE = 'habitat_type'
FIELD_SITE_TREATMENT = 'treatment'
FIELD_SITE_GIS_POINT = 'gis_point'
FIELD_SITE_COUNTRY = 'country'
FIELD_SITE_STATE_REGION = 'state_region'
FIELD_SITE_COUNTY_REGION = 'county_region'
FIELD_SITE_US_STATE_COUNTY_FIPS = 'us_state_county_fips'
FIELD_SITE_LONGITUDE = 'longitude'
FIELD_SITE_LATITUDE = 'latitude'

FIELD_SAMPLE_ID = 'id'
FIELD_SAMPLE_DATE = 'sample_date'
FIELD_SAMPLE_TYPE = 'sample_type'

# Model Defaults

TAXON_CLASS_ACARI = 'acari'
TAXON_CLASS_ANNELIDA = 'annelida'
TAXON_CLASS_COLLEMBOLA = 'collembola'
TAXON_CLASS_GASTROPODA = 'gastropoda'
TAXON_CLASS_NEMATODA = 'nematoda'
TAXON_CLASS_THYSANOPTERA = 'thysanoptera'


def sample_taxon_classes_default():
    return dict(
        TAXON_CLASS_ACARI=0,
        TAXON_CLASS_ANNELIDA=0,
        TAXON_CLASS_COLLEMBOLA=0,
        TAXON_CLASS_GASTROPODA=0,
        TAXON_CLASS_NEMATODA=0,
        TAXON_CLASS_THYSANOPTERA=0
    )


#  Model Choices

ACCEPTANCE_PENDING = 0
ACCEPTANCE_CONFIRMED = 1
ACCEPTANCE_REJECTED = 2

ACCEPTANCE_CHOICES = (
    (ACCEPTANCE_PENDING, 'Pending'),
    (ACCEPTANCE_CONFIRMED, 'Confirmed'),
    (ACCEPTANCE_REJECTED, 'Rejected'),
)


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
SAMPLE_TYPE_VEGETATION_SWEEP = 'vegetation_sweep'

SAMPLE_TYPE_CHOICES = (
    BLANK_CHOICE_DASH[0],
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
    (SAMPLE_TYPE_VEGETATION_SWEEP, 'Vegetation sweep'),
)

SAMPLE_TYPE_CHOICES_WO_BLANK = (v for v in SAMPLE_TYPE_CHOICES if v != BLANK_CHOICE_DASH[0])

SAMPLE_TYPE_CHOICES_DICT = {v[0]: v[1] for v in SAMPLE_TYPE_CHOICES}

SITE_HABITAT_TYPES = [
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
    'corn',
    'cover crop',
    'dairy',
    'flax',
    'goat',
    'green beans',
    'hay',
    'kernza',
    'lentils',
    'livestock',
    'milo',
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
]

SITE_HABITAT_TYPE_CHOICES = ((v, v.capitalize()) for v in SITE_HABITAT_TYPES)

SITE_HABITAT_TYPE_CHOICES_W_BLANK = tuple(chain((BLANK_CHOICE_DASH[0],), SITE_HABITAT_TYPE_CHOICES))

SITE_TREATMENT_TYPES = (
    'conventional',
    'regenerative',
    'transitional',
    'unknown',
    'not in list',
)

SITE_TREATMENT_CHOICES = ((v, v.capitalize()) for v in SITE_TREATMENT_TYPES)

SITE_TREATMENT_CHOICES_W_BLANK = tuple(chain((BLANK_CHOICE_DASH[0],), SITE_TREATMENT_CHOICES))

#  Form Fields

FORM_FIELDS_EXPERIMENT = [
    FIELD_NAME,
    FIELD_ABBREVIATION,
    FIELD_FROM_YEAR,
    FIELD_TO_YEAR,
    FIELD_LEADER,
    FIELD_COMPLETED,
    FIELD_SUMMARY,
    FIELD_NO_SITES,
    FIELD_DATE_PER_SITE
]

FORM_FIELDS_SAMPLE_PLAN = [
    FIELD_SAMPLE_PLAN_ID,
    FIELD_SAMPLE_PLAN_SAMPLE_TYPE,
    FIELD_SAMPLE_PLAN_NO_PER_DATE,
    FIELD_SAMPLE_PLAN_NAME_NO_PER_TYPE
]


FORM_FIELDS_SITE = [
    FIELD_SITE_SITE_NAME,
    FIELD_SITE_HABITAT_TYPE,
    FIELD_SITE_TREATMENT,
    FIELD_SITE_LONGITUDE,
    FIELD_SITE_LATITUDE
]

FORM_FIELDS_SAMPLE = [
    FIELD_SAMPLE_DATE,
    FIELD_SAMPLE_TYPE
]

# Required Fields

FORM_FIELDS_EXPERIMENT_REQUIRED = [
    FIELD_NAME,
    FIELD_FROM_YEAR,
    FIELD_TO_YEAR,
    FIELD_LEADER,
    FIELD_NO_SITES,
    FIELD_DATE_PER_SITE
]

# Field Labels

FORM_FIELDS_EXPERIMENT_LABELS = {
        FIELD_NAME: 'Experiment Name',
        FIELD_LEADER: 'Experiment Leader',
        FIELD_NO_SITES: 'Number of Sites',
        FIELD_DATE_PER_SITE: 'Sample Dates/Site',
    }

FORM_FIELDS_SAMPLE_PLAN_LABELS = {
    FIELD_SAMPLE_PLAN_NO_PER_DATE: 'Number per Date',
    FIELD_SAMPLE_PLAN_NAME_NO_PER_TYPE: 'Name/No.'
}
