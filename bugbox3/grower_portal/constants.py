GENDER_CHOICES = [
    ('male', 'Male'),
    ('female', 'Female'),
    ('prefer_not_to_say', 'Prefer not to say'),
]

RACE_CHOICES = [
    ('american_indian_alaska_native', 'American Indian or Alaska Native'),
    ('asian', 'Asian'),
    ('black_african_american', 'Black or African American'),
    ('native_hawaiian_pacific_islander', 'Native Hawaiian or Other Pacific Islander'),
    ('white', 'White'),
    ('two_or_more_races', 'Two or More Races'),
    ('prefer_not_to_say', 'Prefer not to say'),
]

FIELD_TYPE_CHOICES = [
    ('crop', 'Crop field'),
    ('orchard', 'Orchard/vineyard/woody crop'),
    ('range', 'Rangeland/pasture'),
]

TRANSITIONAL_STATUS_CHOICES = [
    ('1st_year', '1st year'),
    ('2nd_year', '2nd year'),
    ('3rd_year', '3rd year'),
    ('4th_year', '4th year'),
]

INSECTICIDE_FREQUENCY_CHOICES = [
    ('not_used', 'Not used/less than 10% of herd'),
    ('once_per_year', 'Once per year, not during grazing'),
    ('multiple_times', 'Multiple times per year, and/or during grazing season'),
]

CSV_IMPORT_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('processing', 'Processing'),
    ('completed', 'Completed'),
    ('failed', 'Failed'),
]

DEFAULT_FIELD_LATITUDE = 44.3114
DEFAULT_FIELD_LONGITUDE = -96.7984


GOOGLE_MAPS_VERSION = 'weekly'
GOOGLE_MAPS_CALLBACK_INTERACTIVE = 'initMap'
GOOGLE_MAPS_CALLBACK_READONLY = 'initMapView'

AGE_MIN = 1
AGE_MAX = 120

LATITUDE_MIN = -90
LATITUDE_MAX = 90
LONGITUDE_MIN = -180
LONGITUDE_MAX = 180

GRAZING_EVENT_NUMBER_MIN = 1
GRAZING_EVENT_NUMBER_MAX = 4

REST_PERIOD_DAYS_MIN = 0
REST_PERIOD_DAYS_MAX = 365

NUMBER_OF_ANIMALS_MIN = 1
NUMBER_OF_ANIMALS_MAX = 10000

AVERAGE_WEIGHT_MIN = 1
AVERAGE_WEIGHT_MAX = 5000

DURATION_DAYS_MIN = 1
DURATION_DAYS_MAX = 365

ACRES_SAMPLED_MIN = 0.1
ACRES_SAMPLED_MAX = 10000
YEARS_UNDER_MANAGEMENT_MIN = 0
YEARS_UNDER_MANAGEMENT_MAX = 500

# Field Length Constants
PHONE_MAX_LENGTH = 20
FARM_NAME_MAX_LENGTH = 200
FIELD_NAME_MAX_LENGTH = 200
CROP_VARIETY_MAX_LENGTH = 200
CROP_VARIETIES_MAX_LENGTH = 500 
MAX_ANIMAL_ENTRIES_PER_GRAZING_EVENT = 10
FORAGE_VARIETIES_MAX_LENGTH = 500
PADDOCK_SIZE_MAX_LENGTH = 100
ROOTSTOCK_SPECIES_MAX_LENGTH = 500
TILLAGE_DEPTH_MAX_LENGTH = 50
TILLAGE_METHODS_MAX_LENGTH = 500
COVER_CROP_TERMINATION_MAX_LENGTH = 100
ORGANIC_AMENDMENT_TYPES_MAX_LENGTH = 500
GRAZER_TYPES_MAX_LENGTH = 200
INSECTICIDE_FREQUENCY_MAX_LENGTH = 100
INSECTICIDE_COMMENTS_MAX_LENGTH = 100
GROUND_COVER_MANAGEMENT_MAX_LENGTH = 100
TRANSECT_CODE_MAX_LENGTH = 20
SUBMISSION_CODE_MAX_LENGTH = 50
CLASS_OF_ANIMAL_MAX_LENGTH = 100
CSV_FILENAME_MAX_LENGTH = 255
STATUS_MAX_LENGTH = 50
FILE_PATH_MAX_LENGTH = 255

# Submission Code Generation Constants
SUBMISSION_CODE_PREFIX = 'APP'
FIELD_INITIALS_MAX_LENGTH = 3
GROWER_INITIALS_MAX_LENGTH = 2
GROWER_INITIALS_DEFAULT = 'GR'
UUID_SUFFIX_LENGTH = 8

# Grazing Events Constants
MAX_GRAZING_EVENTS = 4
DEFAULT_YEAR = 2025

# Crop Type Choices
CROP_TYPE_CHOICES = [
    ('row_crop', 'Row crop'),
    ('mixed_veg', 'Mixed Vegetables/herbs/specialty crops'),
    ('hayfield', 'Hayfield/Cover crop'),
    ('cash_crop_cover', 'Cash crop with cover crop'),
]

# Orchard Crop Type Choices
ORCHARD_CROP_TYPE_CHOICES = [
    ('fruit_trees', 'Fruit trees'),
    ('nut_trees', 'Nut trees'),
    ('grapes', 'Grapes'),
    ('blueberries', 'Blueberries'),
]

CROP_SUBTYPE_CHOICES = [
    ('corn', 'Corn'),
    ('soybean', 'Soybean'),
    ('small_grain', 'Small grain'),
    ('potato', 'Potato'),
    ('peanut', 'Peanut'),
    ('other', 'Other'),
]

# Cover Crop Termination Choices
COVER_CROP_TERMINATION_CHOICES = [
    ('grazing', 'Grazing'),
    ('mowing', 'Mowing'),
    ('tillage', 'Tillage'),
    ('herbicide', 'Herbicide'),
    ('other', 'Other'),
]

# Organic Amendment Choices
ORGANIC_AMENDMENT_CHOICES = [
    ('manure', 'Manure'),
    ('compost', 'Compost'),
    ('compost_tea', 'Compost tea'),
    ('organic_fertilizer', 'Organic fertilizer'),
    ('other', 'Other'),
]

# Grazer Types Choices
GRAZER_TYPES_CHOICES = [
    ('cattle', 'Cattle'),
    ('sheep', 'Sheep'),
    ('goats', 'Goats'),
    ('hogs', 'Hogs'),
    ('chickens', 'Chickens'),
    ('other', 'Other'),
]

# Ground Cover Management Choices
GROUND_COVER_MANAGEMENT_CHOICES = [
    ('grazing', 'Grazing'),
    ('mowing', 'Mowing'),
    ('tilling', 'Tilling'),
    ('herbicide', 'Herbicide'),
    ('other', 'Other'),
]

# Form Help Text Constants
CLASS_OF_ANIMAL_EXAMPLES = 'Examples: Cow/calf pair, yearling cattle (7-12 months), yearling cattle (12-17 months), replacement heifers (18-24 months), bull, ewe/lamb pair, non-lactating ewe, ram, wether, bison cow, bison bull, etc.'

# Measurements step constants
DISTANCES_DROP_PLATE = [i for i in range(0, 49, 2)]  # 0,2,...,48
POSITIONS_3POINT = [0, 25, 50]
INFILTROMETER_TIMES = [
    "0:00", "0:30", "1:00", "1:30", "2:00", "2:30",
    "3:00", "3:30", "4:00", "4:30", "5:00"
]

FIELD_CONDITION_CHOICES = [
    ('wet', 'Wet'),
    ('dry', 'Dry'),
    ('average', 'Average'),
]

VEGETATION_METRIC_CHOICES = [
    ('green_cover', 'Green Cover %'),
    ('total_groundcover', 'Total Groundcover %'),
    ('plant_richness_no_crop', 'Plant Species Richness (no crops)'),
    ('plant_richness_with_crop', 'Plant Species Richness (with crops)'),
]

SOIL_METRIC_CHOICES = [
    ('moisture_pct', 'Soil Moisture %'),
    ('temp_c', 'Soil Temperature (°C)'),
]

# CSV Import Schema Configuration
CSV_IMPORT_SCHEMAS = {
    'haney': {
        'name': 'Haney',
        'required_headers': [
            'Cust ID',
            'Name',
            'Company',
            'Address 1',
            'Address 2',
            'City',
            'ST',
            'Zip',
            'Date Recd',
            'Date Rept',
            'Lab No',
            'Grower',
            'Field ID',
        ],
    },
    'plfa': {
        'name': 'PLFA',
        'required_headers': [
            'Sample Type',
            'Lab ID',
            'Test ID',
            'Date Received',
            'Date Reported',
            'Customer ID',
            'Name',
            'Company',
            'Grower',
            'Field ID',
        ],
    },
    'basic': {
        'name': 'Basic',
        'required_headers': [
            'Sample Type',
            'Lab No',
            'Test ID',
            'Date Recd',
            'Date Rept',
            'Cust ID',
            'Name',
            'Company',
            'Grower',
            'Field ID',
        ],
    },
}

LABEL_PROJECT_CHOICES = [
    ('avalanche', 'Avalanche'),
    ('1000_farms', '1000 Farms'),
]

LABEL_CATEGORY_CHOICES = [
    ('inner', 'Inner labels'),
    ('outer', 'Outer labels'),
]

SAMPLE_TYPES = [
    ('soil_core_0_60cm', 'Soil core 0-60cm'),
    ('soil_core_0_5cm', 'Soil core 0-5cm'),
    ('soil_core_5_10cm', 'Soil core 5-10cm'),
    ('soil_core_10_15cm', 'Soil core 10-15cm'),
    ('soil_core_15_30cm', 'Soil core 15-30cm'),
    ('soil_core_30_60cm', 'Soil core 30-60cm'),
    ('soil_core_0_15cm', 'Soil core 0-15cm'),
    ('soil_archive', 'Soil archive'),
    ('insect_quads', 'Insect quads'),
    ('insect_sweeps', 'Insect sweeps'),
    ('plant_dna', 'Plant DNA'),
    ('bulk_density', 'Bulk density'),
    ('forage', 'Forage'),
    ('yield_sample', 'Yield/Crop Sample'),
]

LABEL_COUNT_MIN = 1
LABEL_COUNT_MAX = 1000
CLUSTER_NUMBER_MAX_LENGTH = 10
LABEL_FILE_MAX_LENGTH = 255
LABEL_DESCRIPTION_MAX_LENGTH = 500
LABEL_TEMPLATE_SLUG = 'labels-template'
SUBMITTAL_TEMPLATE_SLUG = 'submittal-soil-template'
SUBMITTAL_PLANT_TEMPLATE_SLUG = 'submittal-plant-template'

SUBMITTAL_TEST_ID_SOIL = 'BASIC-TOC-TC-TN-SOIL MOISTURE'
SUBMITTAL_TEST_ID_SH = 'HANEY-PLFA-AG STABILITY-TEXTURE-BeCrop'
SUBMITTAL_TEST_ID_PLANT = 'CC Routine'

SUBMITTAL_SH_START_DEPTH = 0
SUBMITTAL_SH_END_DEPTH = 15
SUBMITTAL_SH_INCHES_START = 0
SUBMITTAL_SH_INCHES_END = 6

SUBMITTAL_PLANT_TYPE = 'forage mix'