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

FIELD_SITE_EXPERIMENT_ID = 'experiment'
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

FIELD_SITE_VISIT_ID = 'id'
FIELD_SITE_VISIT_SITE = 'site'
FIELD_SITE_VISIT_DATE = 'visit_date'
FIELD_SITE_VISIT_USER = 'created_by_user'
FIELD_SITE_VISIT_USER_ID = 'created_by_user_id'

FIELD_SAMPLE_ID = 'id'
FIELD_SAMPLE_TYPE = 'sample_type'
FIELD_SAMPLE_NAME_NO = 'name_no'
FIELD_SAMPLE_NOTES = 'notes'
FIELD_SAMPLE_COMPLETED = 'completed'
FIELD_SAMPLE_IMAGE = 'image'

FIELD_SPECIMEN_CLASSIFICATION = 'classification'
FIELD_SPECIMEN_CLASSIFICATION_ID = 'classification_id'
FIELD_SPECIMEN_AI_CLASSIFICATION = 'ai_classification'
FIELD_SPECIMEN_AI_VERSION = 'ai_version'
FIELD_SPECIMCEN_SAMPLE = 'sample'
FIELD_SPECIMEN_UUID = 'uuid'
FIELD_SPECIMEN_PARTIAL_COUNT = 'partial_count'
FIELD_SPECIMEN_DATE_ADDED = 'date_added'
FIELD_SPECIMEN_DATE_MODIFIED = 'date_modified'
FIELD_SPECIMEN_CONFIDENCE = 'confidence'
FIELD_SPECIMEN_OPTIONAL_PRED_ONE = 'optional_pred_one'
FIELD_SPECIMEN_OPTIONAL_PRED_TWO = 'optional_pred_two'

FIELD_SPECIMEN_OPTIONAL_PRED_ONE_CLASS_OP = 'optional_pred_one__class_op'
FIELD_SPECIMEN_OPTIONAL_PRED_ONE_PRED_OP = 'optional_pred_one__pred_op'
FIELD_SPECIMEN_OPTIONAL_PRED_TWO_CLASS_OP = 'optional_pred_two__class_op'
FIELD_SPECIMEN_OPTIONAL_PRED_TWO_PRED_OP = 'optional_pred_two__pred_op'

FIELD_SPECIMEN_TAGS = 'tags'
FIELD_SPECIMEN_ACCEPTANCE = 'acceptance'
FIELD_SPECIMEN_ARCHIVAL_IDENTIFIER = 'archival_identifier'
FIELD_SPECIMEN_ARCHIVAL_PRESERVATION = 'archival_preservation'
FIELD_SPECIMEN_ARCHIVAL_STORED = 'archival_stored'

FIELD_TIMELINE_EVENT_SPECIMEN = 'specimen'
FIELD_TIMELINE_EVENT_BY_USER = 'by_user'
FIELD_TIMELINE_EVENT_EVENT_TITLE = 'event_title'
FIELD_TIMELINE_EVENT_DATE_TIME = 'date_time'
FIELD_TIMELINE_EVENT_BODY = 'body'

TABLE_SAMPLE = 'sample__'
TABLE_SITE_VISIT = 'site_visit__'
TABLE_SITE = 'site__'
TABLE_EXPERIMENT = 'experiment__'

EXPERIMENT_FROM_SAMPLE = TABLE_SAMPLE + TABLE_SITE_VISIT + TABLE_SITE + TABLE_EXPERIMENT
SITE_FROM_SAMPLE = TABLE_SAMPLE + TABLE_SITE_VISIT + TABLE_SITE
SITE_VISIT_FROM_SAMPLE = TABLE_SAMPLE + TABLE_SITE_VISIT

SAMPLE_IMAGE_THUMBSIZE = 250
SPECIMEN_IMAGE_THUMBSIZE = 50
SPECIMEN_IMAGE_THUMBSIZE_MEDIUM = 350
SPECIMEN_IMAGE_THUMBSIZE_LARGE = 650

SPECIMEN_IMAGE_PRIMARY = 'primary_image'
SPECIMEN_IMAGE_IMAGE = 'image'
SPECIMEN_IMAGE_IMAGE_THUMBNAIL = 'image_thumbnail'
SPECIMEN_IMAGE_IMAGE_THUMBNAIL_MEDIUM = 'image_thumbnail_medium'
SPECIMEN_IMAGE_DATE_ADDED = 'date_added'

#  Model Choices

ACCEPTANCE_PENDING = 0
ACCEPTANCE_CONFIRMED = 1
ACCEPTANCE_REJECTED = 2

ACCEPTANCE_CHOICES = (
    (ACCEPTANCE_PENDING, 'Pending'),
    (ACCEPTANCE_CONFIRMED, 'Confirmed'),
    (ACCEPTANCE_REJECTED, 'Rejected'),
)

ACCEPTANCE_VALUE_LOOKUP = {v[1]: v[0] for v in ACCEPTANCE_CHOICES}
ACCEPTANCE_LOOKUP = {v[0]: v[1] for v in ACCEPTANCE_CHOICES}


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

SAMPLE_TYPE_CHOICES_ALL = [v[0] for v in SAMPLE_TYPE_CHOICES]

SAMPLE_TYPE_CHOICES_WO_BLANK = [v for v in SAMPLE_TYPE_CHOICES if v != BLANK_CHOICE_DASH[0]]

SAMPLE_TYPE_CHOICES_DICT = {v[0]: v[1] for v in SAMPLE_TYPE_CHOICES}

INDICES_CHOICES = (
    ('abundance', "Abundance"),
    ('species_richness', "Species Richness"),
    ('shannons_h', "Shannon's H"),
    ('simpsons', "Simpson's (1-D)"),
    ('hill_shannon', "Hill-Shannon"),
    ('hill_simpson', "Hill-Simpson"),
)

INDICES_CHOICES_ALL = [v[0] for v in INDICES_CHOICES]

INDICES_CHOICES_DICT = {v[0]: v[1] for v in INDICES_CHOICES}

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
)

SITE_HABITAT_TYPE_CHOICES = [(v, v.capitalize()) for v in SITE_HABITAT_TYPES]

SITE_HABITAT_TYPE_CHOICES_W_BLANK = tuple(chain((BLANK_CHOICE_DASH[0],), SITE_HABITAT_TYPE_CHOICES))

SITE_TREATMENT_TYPES = (
    'conventional',
    'regenerative',
    'transitional',
    'unknown',
    'not in list',
)

SITE_TREATMENT_CHOICES = [(v, v.capitalize()) for v in SITE_TREATMENT_TYPES]

SITE_TREATMENT_CHOICES_W_BLANK = tuple(chain((BLANK_CHOICE_DASH[0],), SITE_TREATMENT_CHOICES))

#  Form Fields

FORM_FIELDS_EXPERIMENT = (
    FIELD_NAME,
    FIELD_ABBREVIATION,
    FIELD_FROM_YEAR,
    FIELD_TO_YEAR,
    FIELD_LEADER,
    FIELD_COMPLETED,
    FIELD_SUMMARY,
    FIELD_NO_SITES,
    FIELD_DATE_PER_SITE
)

FORM_FIELDS_SAMPLE_PLAN = (
    FIELD_SAMPLE_PLAN_ID,
    FIELD_SAMPLE_PLAN_SAMPLE_TYPE,
    FIELD_SAMPLE_PLAN_NO_PER_DATE,
    FIELD_SAMPLE_PLAN_NAME_NO_PER_TYPE
)

FORM_FIELDS_SITE = (
    FIELD_SITE_EXPERIMENT_ID,
    FIELD_SITE_SITE_NAME,
    FIELD_SITE_HABITAT_TYPE,
    FIELD_SITE_TREATMENT,
    FIELD_SITE_LONGITUDE,
    FIELD_SITE_LATITUDE
)

FORM_FIELDS_SITE_VISIT = (
    FIELD_SITE_VISIT_DATE,
    FIELD_SITE_VISIT_ID
)

FORM_FIELDS_SITE_VISIT_HIDDEN = (
    FIELD_SITE_VISIT_ID
)

FORM_FIELDS_SAMPLE = (
    FIELD_SAMPLE_TYPE,
    FIELD_SAMPLE_NAME_NO,
    FIELD_SAMPLE_NOTES,
    FIELD_SAMPLE_COMPLETED,
    FIELD_SAMPLE_IMAGE,
)

FORM_FIELDS_SPECIMEN = (
    FIELD_SPECIMCEN_SAMPLE,
    FIELD_SPECIMEN_CLASSIFICATION,
    FIELD_SPECIMEN_PARTIAL_COUNT,
    FIELD_SPECIMEN_TAGS,
    FIELD_SPECIMEN_ACCEPTANCE,
    FIELD_SPECIMEN_ARCHIVAL_IDENTIFIER,
    FIELD_SPECIMEN_ARCHIVAL_PRESERVATION,
    FIELD_SPECIMEN_ARCHIVAL_STORED,
)

FORM_FIELDS_SPECIMEN_HIDDEN = (
    FIELD_SPECIMEN_CLASSIFICATION,
    FIELD_SPECIMCEN_SAMPLE
)

# Required Fields

FORM_FIELDS_EXPERIMENT_REQUIRED = (
    FIELD_NAME,
    FIELD_FROM_YEAR,
    FIELD_TO_YEAR,
    FIELD_LEADER,
    FIELD_NO_SITES,
    FIELD_DATE_PER_SITE
)

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

FORM_FIELDS_SPECIMEN_LABELS = {
    FIELD_SPECIMEN_ARCHIVAL_PRESERVATION: 'Preservation',
    FIELD_SPECIMEN_ARCHIVAL_STORED: 'Stored',
    FIELD_SPECIMEN_ACCEPTANCE: 'AI Acceptance'
}

# HELP TEXT

FORM_FIELDS_SPECIMEN_HELP = {
    FIELD_SPECIMEN_TAGS: 'use cmd/ctrl + click to select multiple',
    FIELD_SPECIMEN_ACCEPTANCE: 'if acceptance is "Confirmed" the AI Prediction '
                               'will be saved as the "Verified classification"'
}

TAGS = (
    'adult'
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
    'pollinator',
    'pupa',
    'queen',
    'teneral',
    'worker',
    'worker (major)'
)

TAG_CHOICES = ((v, v) for v in TAGS)

# PERMISSIONS
PERMISSION_SPECIMEN_REVIEW = 'review_specimen_page'
PERMISSION_SPECIMEN_REVIEW_TXT = 'Can use the review specimen page.'


# EXPORTS
EXPERIMENT_AI_CSV = [
    EXPERIMENT_FROM_SAMPLE + FIELD_NAME,
    FIELD_SPECIMEN_UUID,
    FIELD_SPECIMEN_CLASSIFICATION + '__name',
    FIELD_SPECIMEN_CLASSIFICATION + '__gbif_class',
    FIELD_SPECIMEN_CLASSIFICATION + '__gbif_order',
    FIELD_SPECIMEN_CLASSIFICATION + '__gbif_family',
    FIELD_SPECIMEN_CLASSIFICATION + '__gbif_canonical_name',
    FIELD_SPECIMEN_AI_VERSION + '__version',
    FIELD_SPECIMEN_AI_CLASSIFICATION + '__name',
    FIELD_SPECIMEN_CONFIDENCE,
    FIELD_SPECIMEN_OPTIONAL_PRED_ONE_CLASS_OP,
    FIELD_SPECIMEN_OPTIONAL_PRED_ONE_PRED_OP,
    FIELD_SPECIMEN_OPTIONAL_PRED_TWO_CLASS_OP,
    FIELD_SPECIMEN_OPTIONAL_PRED_TWO_PRED_OP,
]

EXP_HEAD_ARR_EXPERIMENT = 'Experiment'
EXP_HEAD_ARR_SITE = 'Site'
EXP_HEAD_ARR_DATE = 'Date'
EXP_HEAD_ARR_SAMPLE_TYPE = 'Sample Type'
EXP_HEAD_ARR_SAMPLE_NAME = 'Sample Name'
EXP_HEAD_ARR_SAMPLE_COMPLETED = 'Marked completed'
EXP_HEADERS_ARR = [
    EXP_HEAD_ARR_EXPERIMENT,
    EXP_HEAD_ARR_SITE,
    EXP_HEAD_ARR_DATE,
    EXP_HEAD_ARR_SAMPLE_TYPE,
    EXP_HEAD_ARR_SAMPLE_NAME,
    EXP_HEAD_ARR_SAMPLE_COMPLETED
]

EXP_CSV_TYPE_ALL = 'all'
EXP_CSV_TYPE_REVIEWED = 'reviewed-only'
EXP_CSV_TYPE_AI = 'ai-only'
EXPERIMENT_CSV_EXPORT_CHOICES = (
    (EXP_CSV_TYPE_ALL, 'Reviewd and AI (all)'),
    (EXP_CSV_TYPE_REVIEWED, 'Reviewed only'),
    (EXP_CSV_TYPE_AI, 'AI only'),
)

EXPERIMENT_CSV_EXPORT_TYPES = [v[0] for v in EXPERIMENT_CSV_EXPORT_CHOICES]

# TimelineEvent
TIMELINEEVENT_REVIEW = 'Review'
