from ..samples.constants import (FIELD_SAMPLE_TYPE, FIELD_SITE_HABITAT_TYPE,
                                 FIELD_SITE_TREATMENT, FIELD_SPECIMEN_TAGS)
from ..taxonomy.constants import FIELD_MORPHO_TAGS_LOOKUP

# LookupChoices

FIELD_FIELD = 'field'
FIELD_ENTRY = 'entry'
FIELD_DISPLAY_TXT = 'display_txt'

VALID_LOOKUP_FIELDS = [
    FIELD_SITE_HABITAT_TYPE, FIELD_SITE_TREATMENT,
    FIELD_SAMPLE_TYPE, FIELD_SPECIMEN_TAGS, FIELD_MORPHO_TAGS_LOOKUP
]

# Site

CANADA = 'Canada'
UNITED_STATES = 'United States'

US_STATE_CHOICES = 'US_STATE_CHOICES'
CANADA_STATE_CHOICES = 'CANADA_STATE_CHOICES'

COUNTRY_CHOICES = ((CANADA_STATE_CHOICES, CANADA), (US_STATE_CHOICES, UNITED_STATES))
COUNTRY_LOOKUP = {v[0]: v[1] for v in COUNTRY_CHOICES}

FIPS_STATE = {
    '02': 'AK',
    '01': 'AL',
    '05': 'AR',
    '60': 'AS',
    '04': 'AZ',
    '06': 'CA',
    '08': 'CO',
    '09': 'CT',
    '11': 'DC',
    '10': 'DE',
    '12': 'FL',
    '13': 'GA',
    '66': 'GU',
    '15': 'HI',
    '19': 'IA',
    '16': 'ID',
    '17': 'IL',
    '18': 'IN',
    '20': 'KS',
    '21': 'KY',
    '22': 'LA',
    '25': 'MA',
    '24': 'MD',
    '23': 'ME',
    '26': 'MI',
    '27': 'MN',
    '29': 'MO',
    '28': 'MS',
    '30': 'MT',
    '37': 'NC',
    '38': 'ND',
    '31': 'NE',
    '33': 'NH',
    '34': 'NJ',
    '35': 'NM',
    '32': 'NV',
    '36': 'NY',
    '39': 'OH',
    '40': 'OK',
    '41': 'OR',
    '42': 'PA',
    '72': 'PR',
    '44': 'RI',
    '45': 'SC',
    '46': 'SD',
    '47': 'TN',
    '48': 'TX',
    '49': 'UT',
    '51': 'VA',
    '78': 'VI',
    '50': 'VT',
    '53': 'WA',
    '55': 'WI',
    '54': 'WV',
    '56': 'WY'
}


STATE_CHOICES = {
    US_STATE_CHOICES: [[v, v] for _ , v in FIPS_STATE.items()],
    CANADA_STATE_CHOICES: (('Manitoba', 'Manitoba'), ('Saskatchewan', 'Saskatchewan'))
}


# Stitcher API Constants
STITCHER_GUID = 'guid'
SSTITCHER_EXTRACT_PATH = 'extract_path'
STITCHER_UPLOAD_DIR_NAME = 'upload_dir_name'
STITCHER_PANORAMA_PATH = 'panorama_path'
STITCHER_PANORAMA_WIDTH = 'panorama_width'
STITCHER_PANORAMA_HEIGHT = 'panorama_height'
STITCHER_PANORAMA_CONFIDENCE = 'panorama_confidence'
STITCHER_APPROVED = 'approved'
STITCHER_PREDICTIONS = 'predictions'
STITCHER_PREDICTIONS_TIMESTAMP = 'predictions_timestamp'
STITCHER_PREDICTIONS_COCO = 'predictions_coco'
STITCHER_PREDICTIONS_TIMESTAMP_COCO = 'predictions_timestamp_coco'
STITCHER_SENT_LABEL_STUDIO = 'sent_label_studio'
STITCHER_LABEL_STUDIO_PROJECT = 'label_studio_project'
STITCHER_STITCHING_EXCEPTION = 'stitching_exception'
STITCHER_STITCHING_EXCEPTION_AT = 'stitching_exception_at'
STITCHER_PANORAMA_TIMESTAMP = 'panorama_timestamp'
STITCHER_CREATED_AT = 'created_at'
STITCHER_ANNOTATIONS = 'annotations'
STITCHER_ANNOTATIONS_UPDATED_AT = 'annotations_updated_at'
STITCHER_ANNOTATIONS_SEGMENT = 'annotations_segment'
STITCHER_ANNOTATOR_SEGMENT = 'annotator_segment'
STITCHER_ANNOTATIONS_UPDATED_AT_SEGMENT = 'annotations_updated_at_segment'
STITCHER_BUGBOX_SAMPLE_ID = 'bugbox_sample_id'
STITCHER_NOTA_SAMPLE = 'nota_sample'
STITCHER_BUGBOX_CROPED_SAVED = 'bugbox_croped_saved'

STITCHER_ERROR = 'ERROR'

STITCHER_TIMEFIELDS = [
    STITCHER_STITCHING_EXCEPTION_AT,
    STITCHER_PANORAMA_TIMESTAMP,
    STITCHER_CREATED_AT
]
STITCHER_FORM_IDENT = 'form_ident'
STITCHER_FORM_DEFAULT = 'defaultValue'
STITCHER_FORM_CROPSAVE = 'cropSave'
STITCHER_FORM_REQUIRED_KEYS = [
    STITCHER_PANORAMA_PATH,
    STITCHER_APPROVED,
    STITCHER_ANNOTATIONS_SEGMENT,
    STITCHER_UPLOAD_DIR_NAME
]
STITCHER_LABEL_IMG = 'label_r_001.jpg'
STITCHER_APPROVED_CHOICES = (
        (None, '---'),
        (True, 'Approved'),
        (False, 'Retake')
    )
STITCHER_STATS_LS_PROJECTS = 'label_studio_projects'

# Default LookupChoices
DEFAULT_TAGS = (
    'adult',
    'egg',
    'female',
    'juvenile',
    'larva',
    'male',
    'mummy',
    'nymph',
    'parasite',
    'pupa',
    'queen',
    'worker',
)
DEFAULT_TAG_CHOICES = [(v, v) for v in DEFAULT_TAGS]

DEFAULT_SITE_HABITAT_TYPES = (
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
DEFAULT_SITE_HABITAT_TYPE_CHOICES = [(v, v.capitalize()) for v in DEFAULT_SITE_HABITAT_TYPES]

DEFAULT_SITE_TREATMENT_TYPES = (
    'conventional',
    'regenerative',
    'transitional',
    'unknown',
    'not in list',
)

DEFAULT_SITE_TREATMENT_CHOICES = [(v, v.capitalize()) for v in DEFAULT_SITE_TREATMENT_TYPES]
