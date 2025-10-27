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
    ('hayfield', 'Hayfield'),
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

