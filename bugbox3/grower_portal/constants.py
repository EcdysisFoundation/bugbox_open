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
    ('completed_with_errors', 'Completed with errors'),
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
CLASS_OF_ANIMAL_EXAMPLES = (
    'Examples: Cow/calf pair, yearling cattle (7-12 months), '
    'yearling cattle (12-17 months), replacement heifers (18-24 months), '
    'bull, ewe/lamb pair, non-lactating ewe, ram, wether, bison cow, '
    'bison bull, etc.'
)

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

RESULT_TYPE_CHOICES = [
    ('haney', 'Haney'),
    ('plfa', 'PLFA'),
    ('basic', 'Basic'),
    ('birds', 'Birds'),
    ('water', 'Water'),
    ('plants', 'Plants'),
]

# Data categories
CATEGORY_CHOICES = [
    ('soils',  'Soils'),
    ('water',  'Water'),
    ('plants', 'Plants'),
    ('birds',  'Birds'),
]

CATEGORY_MAX_LENGTH = 20

# map categories to the result types that belong to it
CATEGORY_RESULT_TYPE_MAP = {
    'soils':  ['basic', 'haney', 'plfa'],
    'water':  ['water'],
    'plants': ['plants'],
    'birds':  ['birds'],
}

# lookup: result_type → category
RESULT_TYPE_CATEGORY_MAP = {
    rt: cat
    for cat, rts in CATEGORY_RESULT_TYPE_MAP.items()
    for rt in rts
}

# S3/storage root prefix for all grower portal ingestion files
GROWER_DATA_S3_PREFIX = 'grower_portal_data'

# Bird-specific ingestion constants
BIRD_SITE_CODE_COLUMN = 'Site Code'
BIRD_FAMILY_HEADER_ROW = 0  # 0-indexed Excel row that contains family names
BIRD_DATA_HEADER_ROW = 1    # the row that contains the column headers

LABEL_PROJECT_CHOICES = [
    ('avalanche', 'Avalanche'),
    ('ignite', 'Ignite'),
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

# Ignite inner sample types (Forage is optional; the checkbox on form has to be checked to include it)
IGNITE_INNER_SAMPLE_TYPES = [
    'soil_core_0_60cm',
    'soil_core_0_5cm',
    'soil_core_5_10cm',
    'soil_core_10_15cm',
    'soil_core_15_30cm',
    'soil_core_30_60cm',
    'soil_core_0_15cm',
    'soil_archive',
    'insect_quads',
    'insect_sweeps',
    'plant_dna',
    'bulk_density'
]

IGNITE_OUTER_SAMPLE_TYPES = [
    'soil_core_0_60cm',
    'soil_core_0_15cm',
    'soil_archive',
    'plant_dna',
    'bulk_density'
]
LABEL_FILE_MAX_LENGTH = 255
LABEL_DESCRIPTION_MAX_LENGTH = 500
LABEL_TEMPLATE_SLUG = 'avalanche-inner-labels'
LABEL_OUTER_TEMPLATE_SLUG = 'avalanche-outer-labels'
LABEL_IGNITE_TEMPLATE_SLUG = 'ignite-labels'

# Outer label sample lists for Avalanche
AVALANCHE_ROOM_TEMP_SAMPLES = [
    "Soil Core 0-60 (5 depths)",
    "Soil Bulk Density",
    "Soil Archive",
    "Plant DNA",
    "Insect Quad in vial"
]

AVALANCHE_REFRIGERATED_SAMPLES = [
    "Soil Core 0-15",
    "Insect Sweep bag",
    "Crop samples",
    "Forage samples"
]

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

AVALANCHE_SAMPLE_CODE_COLUMN = 'Sample ID 1'
IGNITE_SAMPLE_CODE_COLUMN = 'Field ID'
IGNITE_SITE_TRANSECT_COLUMN = 'Sample ID 1'

# These columns are used to validate the uploaded CSV matches the selected result type
RESULT_TYPE_SIGNATURE_COLUMNS = {
    'basic': [
        'Soil pH 1:1',
        'CEC, meq/100g',
        'NH4OAc-Potassium, ppm K',
        'Organic Matter, % LOI',
    ],
    'haney': [
        'H3A Nitrate',
        'CO2-C',
        'Soil Health Calculation',
        'H3A Inorganic Nitrogen',
    ],
    'plfa': [
        'Total Living Microbial Biomass, PLFA ng/g',
        'Fungi:Bacteria',
        'Total Bacteria, PLFA ng/g',
        'Functional Group Diversity Index',
    ],
    'birds': [
        'Site Code',
        'Abundance',
        'Richness',
    ],
}

# Maps results display categories to factor names to CSV column names and units
PLFA_FACTOR_MAPPING = {
    'Overview': {
        'Total Biomass': {
            'field_name': 'Total Living Microbial Biomass, PLFA ng/g',
            'units': 'PLFA ng/g',
        },
        'Functional Group Diversity Index': {
            'field_name': 'Functional Group Diversity Index'
        }
    },
    'Community Breakdown': {
        'Total Bacteria': {
            'field_name': 'Total Bacteria, PLFA ng/g',
            'units': 'PLFA ng/g',
        },
        'Total Bacteria %': {
            'field_name': 'Total Bacteria, % of Tot. Biomass',
            'units': '%',
        },
        'Gram +': {
            'field_name': 'Gram Pos Others, PLFA ng/g',
            'units': 'PLFA ng/g',
        },
        'Gram + %': {
            'field_name': 'Gram Pos Others, % of Tot. Biomass',
            'units': '%',
        },
        'Actinomycetes': {
            'field_name': 'Actinomycetes, PLFA ng/g',
            'units': 'PLFA ng/g',
        },
        'Actinomycetes %': {
            'field_name': 'Actinomycetes, % of Tot. Biomass',
            'units': '%',
        },
        'Gram -': {
            'field_name': 'Gram Neg Others, PLFA ng/g',
            'units': 'PLFA ng/g',
        },
        'Gram - %': {
            'field_name': 'Gram Neg Others, % of Tot. Biomass',
            'units': '%',
        },
        'Total Fungi': {
            'field_name': 'Total Fungi, PLFA ng/g',
            'units': 'PLFA ng/g',
        },
        'Total Fungi %': {
            'field_name': 'Total Fungi, % of Tot. Biomass',
            'units': '%',
        },
        'Arbuscular Mycorrhizal Fungi': {
            'field_name': 'Arbuscular Mycorrhizal Fungi, PLFA ng/g',
            'units': 'PLFA ng/g',
        },
        'Arbuscular Mycorrhizal Fungi %': {
            'field_name': 'Arbuscular Mycorrhizal Fungi, % of Tot. Biomass',
            'units': '%',
        },
        'Saprophytic Fungi': {
            'field_name': 'Saprophytic Fungi, PLFA ng/g',
            'units': 'PLFA ng/g',
        },
        'Saprophytic Fungi %': {
            'field_name': 'Saprophytic Fungi, % of Tot. Biomass',
            'units': '%',
        },
        'Protozoa': {
            'field_name': 'Protozoa, PLFA ng/g',
            'units': 'PLFA ng/g',
        },
        'Protozoa %': {
            'field_name': 'Protozoa, % of Tot. Biomass',
            'units': '%',
        },
        'Undifferentiated': {
            'field_name': 'Undifferentiated, PLFA ng/g',
            'units': 'PLFA ng/g',
        },
        'Undifferentiated %': {
            'field_name': 'Undifferentiated, % of Tot. Biomass',
            'units': '%',
        },
    },
    'Ratios': {
        'Fungi:Bacteria': {
            'field_name': 'Fungi:Bacteria',
        },
        'Protozoa:Bacteria': {
            'field_name': 'Protozoa:Bacteria',
        },
        'Gram+:Gram-': {
            'field_name': 'Gram+:Gram-',
        },
        'Sat:Unsat': {
            'field_name': 'Sat:Unsat',
        },
        'Mono:Poly': {
            'field_name': 'Fungi:Bacteria',
        },
        'Pre 16:Cyclo 17': {
            'field_name': 'Pre 16:Cyclo 17',
        },
        'Pre 18:Cyclo 19': {
            'field_name': 'Pre 18:Cyclo 19',
        },
    },
    'Soil Texture': {
        'Sand': {
            'field_name': '% Sand',
            'units': '%'
        },
        'Silt': {
            'field_name': '% Silt',
            'units': '%'
        },
        'Clay': {
            'field_name': '% Clay',
            'units': '%'
        },
        'Soil Texture': {
            'field_name': 'soil texture',
        },
    },
    'Soil Aggregate Stability': {
        'Macroaggregates >0.25mm': {
            'field_name': 'Macroaggregates, % >0.25mm',
            'units': '%'
        },
        'Microaggregates <0.25, >0.053mm': {
            'field_name': 'Microaggregates, % <0.25, >0.053mm',
            'units': '%'
        },
        'Total Aggregates': {
            'field_name': 'Total Aggregates, %',
            'units': '%'
        },
    }
}

HANEY_FACTOR_MAPPING = {
    'Nitrogen (H3A Extract)': {
        'Nitrate': {
            'field_name': 'H3A Nitrate',
            'units': 'ppm NO3-N',
            'summary': 'A short definition of this factor',
            'description': 'A longer definition of the factor to display on the factor detail page.'
        },
        'Ammonium': {
            'field_name': 'H3A Ammonium',
            'units': 'ppm NH4-N'
        },
        'Inorganic Nitrogen': {
            'field_name': 'H3A Inorganic Nitrogen',
            'units': 'ppm N'
        },
    },
    'Nitrogen (H2O Extract)': {
        'Total N': {
            'field_name': 'H2O Total N',
            'units': 'ppm N'
        },
        'Organic N': {
            'field_name': 'H2O Organic N',
            'units': 'ppm N'
        },
        'Total Organic C': {
            'field_name': 'H2O Total Organic C',
            'units': 'ppm C'
        },
        'Organic N Release': {
            'field_name': 'Organic N Release',
            'units': 'ppm N'
        },
        'Organic N Reserve': {
            'field_name': 'Organic N Reserve',
            'units': 'ppm N'
        },
        'Available N': {
            'field_name': 'Available N',
            'units': 'lbs/A'
        }
    },
    'Phosphorous (H3A Extract)': {
        'Total Phosphorous': {
            'field_name': 'H3A Total Phosphorus',
            'units': 'ppm P'
        },
        'Inorganic Phosphorous': {
            'field_name': 'H3A Inorganic Phosphorus',
            'units': 'ppm PO4-P'
        },
        'Organic Phosphorus': {
            'field_name': 'H3A Organic Phosphorus',
            'units': 'ppm P'
        },
        'Organic P Release': {
            'field_name': 'Organic P Release',
            'units': 'ppm P'
        },
        'Organic P Reserve': {
            'field_name': 'Organic P Reserve',
            'units': 'ppm P'
        },
        'Available P': {
            'field_name': 'Available P',
            'units': 'lbs/A'
        }
    },
    'Other Soil Measures': {
        'Soil pH 1:1': {
            'field_name': '1:1 Soil pH',
        },
        'WDRF Buffer': {
            'field_name': 'WDRF Buffer',
        },
        'Soluble Salt': {
            'field_name': '1:1 Soluble Salt',
            'units': 'mmho/cm'
        },
        'Excess Lime': {
            'field_name': 'Excess Lime',
        },
        'Soil Organic Matter': {
            'field_name': 'Organic Matter',
            'units': '% LOI'
        },
    },
    'Fertility (H3A Extract)': {
        'Potassium': {
            'field_name': 'H3A ICAP Potassium',
            'units': 'ppm K'
        },
        'Calcium': {
            'field_name': 'H3A ICAP Calcium',
            'units': 'ppm C'
        },
        'Magnesium': {
            'field_name': 'H3A ICAP Magnesium',
            'units': 'ppm Mg'
        },
        'Sodium': {
            'field_name': 'H3A ICAP Sodium',
            'units': 'ppm Na'
        },
        'Zinc': {
            'field_name': 'H3A ICAP Zinc',
            'units': 'ppm Zn'
        },
        'Manganese': {
            'field_name': 'H3A ICAP Manganese',
            'units': 'ppm Mn'
        },
        'Iron': {
            'field_name': 'H3A ICAP Iron',
            'units': 'ppm Fe'
        },
        'Copper': {
            'field_name': 'H3A ICAP Copper',
            'units': 'ppm Cu'
        },
        'Aluminum': {
            'field_name': 'H3A ICAP Aluminum',
            'units': 'ppm Al'
        },
        'Sulfur': {
            'field_name': 'H3A ICAP Sulfur',
            'units': 'ppm S'
        },
    },
    'Soil Health': {
        'Soil Respiration': {
            'field_name': 'CO2-C',
            'units': 'ppm CO2-C'
        },
        'MAC': {
            'field_name': '% MAC',
            'units': '%'
        },
        'Organic C:N': {
            'field_name': 'Organic C:N',
        },
        'Organic N:Inorganic N': {
            'field_name': 'Organic N:Inorganic N',
        },
        'Soil Health Calculation': {
            'field_name': 'Soil Health Calculation'
        },
        'Cover Crop Mix': {
            'field_name': 'Cover Crop Mix'
        }
    },
    'Nitrogen Comparison': {
        'Traditional N': {
            'field_name': 'Traditional N',
            'units': 'lbs/A'
        },
        'Haney N': {
            'field_name': 'Haney Test N',
            'units': 'lbs/A'
        },
        'Difference N': {
            'field_name': 'Lbs N Difference',
            'units': 'lbs/A'
        },
        'Savings N': {
            'field_name': 'N savings',
            'units': '$/A'
        },
    },
    'Nutrient Availability': {
        'Available K': {
            'field_name': 'Available K',
            'units': 'lbs/A'
        },
        'Nutrient Value': {
            'field_name': 'Nutrient Value',
            'units': '$/A'
        },
    },
}

BASIC_FACTOR_MAPPING = {
    'Soil Analysis': {
        'Soil pH': {
            'field_name': 'Soil pH 1:1',
        },
        'Buffer pH': {
            'field_name': 'Wdrf Buffer',
        },
        '1:1 Electrical Conductivity': {
            'field_name': '1:1 Electrical Conductivity, mmho/cm',
            'units': 'mmho/cm'
        },
        'Excess Lime': {
            'field_name': 'Excess Lime',
        },
        'Organic Matter': {
            'field_name': 'Organic Matter, % LOI',
            'units': '% LOI'
        },
        'Nitrate (ppm)': {
            'field_name': '1N KCl-Nitrate, ppm NO3-N',
            'units': 'ppm NO3-N'
        },
        'Nitrate': {
            'field_name': '1N KCl-Nitrate, lbs/A N',
            'units': 'lbs/A N'
        },
        'Phosphate': {
            'field_name': 'M3-Phosphate, ppm PO4-P',
            'units': 'ppm PO4-P'
        },
        'Sulfur': {
            'field_name': 'M3-Sulfur, ppm S',
            'units': 'ppm S'
        },
        'Potassium': {
            'field_name': 'NH4OAc-Potassium, ppm K',
            'units': 'ppm K'
        },
        'Calcium': {
            'field_name': 'NH4OAc-Calcium, ppm Ca',
            'units': 'ppm Ca'
        },
        'Magnesium': {
            'field_name': 'NH4OAc-Magnesium, ppm Mg',
            'units': 'ppm Mg'
        },
        'Sodium': {
            'field_name': 'NH4OAc-Sodium, ppm Na',
            'units': 'ppm Na'
        },
        'CEC': {
            'field_name': 'CEC, meq/100g',
            'units': 'meq/100g'
        },
        'Base Saturation': {
            'field_name': 'Base Saturation, %',
            'units': '%'
        },
        'Hydrogen Saturation': {
            'field_name': 'Hydrogen, % Sat',
            'units': '%'
        },
        'Calcium Saturation': {
            'field_name': 'Calcium, % Sat',
            'units': '%'
        },
        'Magnesium Saturation': {
            'field_name': 'Magnesium, % Sat',
            'units': '%'
        },
        'Potassium Saturation': {
            'field_name': 'Potassium, % Sat',
            'units': '%'
        },
        'Sodium Saturation': {
            'field_name': 'Sodium, % Sat',
            'units': '%'
        },
        'Total Organic Carbon': {
            'field_name': 'Total Organic Carbon, % C',
            'units': '% C'
        },
        'Total Carbon': {
            'field_name': 'Total Carbon, % C',
            'units': '% C'
        },
        'Total Nitrogen': {
            'field_name': 'Total Nitrogen, % N',
            'units': '% N'
        },
        'Dry Weight': {
            'field_name': 'Total Dry Weight (g)',
            'units': 'g'
        },
    }
}

BIRD_FACTOR_MAPPING = {
    'Survey Summary': {
        'Total Abundance': {
            'field_name': 'Abundance',
            'units': 'individuals',
            'summary': 'Total number of individual birds counted across all surveys for this site.',
        },
        'Species Richness': {
            'field_name': 'Richness',
            'units': 'species',
            'summary': 'Number of distinct bird species observed across all surveys for this site.',
        },
    },
    'Survey Conditions': {
        'Temperature (°F)': {
            'field_name': 'Temp °F',
            'units': '°F',
        },
        'Distance (mi)': {
            'field_name': 'Distance mi',
            'units': 'mi',
        },
        'Duration (min)': {
            'field_name': 'Duration (min)',
            'units': 'min',
        },
    },
}

# Maps result types to their factor mappings
RESULT_TYPE_FACTOR_MAPPING = {
    'plfa': PLFA_FACTOR_MAPPING,
    'haney': HANEY_FACTOR_MAPPING,
    'basic': BASIC_FACTOR_MAPPING,
    'birds': BIRD_FACTOR_MAPPING,
}

# Category display metadata
CATEGORY_DISPLAY_META = {
    'soils': {
        'icon': 'fa-mountain',
        'description': 'Basic, Haney, and PLFA soil test results.',
    },
    'water': {
        'icon': 'fa-tint',
        'description': 'Water infiltration, holding capacity, and conductivity.',
    },
    'plants': {
        'icon': 'fa-leaf',
        'description': 'Plant biomass, cover, and forage data.',
    },
    'birds': {
        'icon': 'fa-dove',
        'description': 'Bird point-count survey data including species richness and abundance.',
    },
}
