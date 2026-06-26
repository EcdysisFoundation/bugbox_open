GENDER_CHOICES = [
    ('male', 'Male'),
    ('female', 'Female'),
    ('prefer_not_to_say', 'Prefer not to say'),
]

RACE_CHOICES = [
    ('white_european', 'White / European'),
    ('black_african_diaspora', 'Black / African / African diaspora'),
    ('indigenous_first_nations_native', 'Indigenous / First Nations / Native'),
    ('east_southeast_asian', 'East or Southeast Asian'),
    ('south_asian', 'South Asian'),
    ('middle_eastern_north_african', 'Middle Eastern / North African'),
    ('latin_american_hispanic_latinx', 'Latin American / Hispanic / Latinx'),
    ('pacific_islander', 'Pacific Islander'),
    ('multiple_backgrounds', 'Multiple backgrounds'),
    ('another_background', 'Another background'),
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
RACE_OTHER_MAX_LENGTH = 200
RACE_INDIGENOUS_COUNTRY_MAX_LENGTH = 2
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
    ('insects', 'Insects'),
    ('water', 'Water'),
    ('plants', 'Plants'),
]

# Data categories
CATEGORY_CHOICES = [
    ('soils',  'Soils'),
    ('water',  'Water'),
    ('plants', 'Plants'),
    ('birds',  'Birds'),
    ('insects', 'Insects'),
]

CATEGORY_MAX_LENGTH = 20

# map categories to the result types that belong to it
CATEGORY_RESULT_TYPE_MAP = {
    'soils':  ['basic', 'haney', 'plfa'],
    'water':  ['water'],
    'plants': ['plants'],
    'birds':  ['birds'],
    'insects': ['insects'],
}

# lookup: result_type → category
RESULT_TYPE_CATEGORY_MAP = {
    rt: cat
    for cat, rts in CATEGORY_RESULT_TYPE_MAP.items()
    for rt in rts
}

# PublicSiteContent sheet PDFs (grower results page)
CATEGORY_FACT_SHEETS = {
    'insects': [
        {'slug': 'factsheet-insects', 'label': 'Insects'},
    ],
    'birds': [
        {'slug': 'factsheet-birds', 'label': 'Bird Counts on Farms'},
    ],
    'soils': [
        {'slug': 'factsheet-soil-physical', 'label': 'Soil (Physical)'},
        {'slug': 'factsheet-soil-nutrition', 'label': 'Soil Nutritional & Chemical Properties'},
        {'slug': 'factsheet-soil-organic-matter', 'label': 'Soil Organic Matter and Carbon'},
    ],
}

# S3/storage root prefix for all grower portal ingestion files
GROWER_DATA_S3_PREFIX = 'grower_portal_data'

# Grower bird recording uploads
BIRD_RECORDING_MAX_BYTES = 250 * 1024 * 1024  # 250 MB per file
BIRD_RECORDING_MAX_BYTES_PER_CODE = 1024 * 1024 * 1024  # 1 GB per grower + sample code
BIRD_RECORDING_PRESIGNED_EXPIRY_SECONDS = 900  # 15 minutes
BIRD_RECORDING_ALLOWED_CONTENT_TYPES = frozenset({
    'audio/wav',
    'audio/x-wav',
    'audio/wave',
    'audio/mpeg',
    'audio/mp3',
    'audio/mp4',
    'video/mp4',  # some browsers report .mp4 audio this way
    'application/octet-stream',  # some browsers for .wav
})
BIRD_RECORDING_ALLOWED_EXTENSIONS = frozenset({
    '.wav', '.mp3', '.mp4',
})

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
    'bulk_density',
    'crop_type_variety',
]

# Ignite outer-only types
IGNITE_OUTER_ONLY_SAMPLE_TYPE_LABELS = {
    'crop_type_variety': 'Crop Type / Variety (yield)',
}

IGNITE_OUTER_CROP_TYPE_VARIETY_CODE = 'crop_type_variety'
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
    'insects': {
        'icon': 'fa-bug',
        'description': 'Insect sampling from BugBox including abundance and species richness by family.',
    },
}

INSECT_EXPORT_LEVEL = 'family'
INSECT_MORPHO_EXPORT_LEVEL = 'morphospecies'
INSECT_GALLERY_AI_MIN_CONFIDENCE = 5  # AI-only specimens below this are excluded from the grower bug gallery
INSECT_GALLERY_MAX_PER_SITE = 12  # round-robin across families

GROWER_TAXONOMY_UNSPECIFIED_CLASS = 'Unspecified class'
GROWER_TAXONOMY_UNSPECIFIED_ORDER = 'Unspecified order'
GROWER_ACARI_SUBCLASS_KEY = 'Acari'
GROWER_ACARI_MITE_MORPHO_NAME = 'Acari'
GROWER_ACARI_MITE_GBIF_ORDERS = frozenset({
    'Astigmata',
    'Mesostigmata',
    'Prostigmata',
    'Sarcoptiformes',
    'Trombidiformes',
    'Oribatida',
    'Ixodida',
})

# for Grower Portal Bugs results: morphospecies with blank gbif_family map to a display group below
# in Export CSV those are counted towards "Unspecified Family" for those morphos
GROWER_FAMILY_DISPLAY_GROUPS = (
    ('Amphipods', ('Amphipoda 001',)),
    ('Beetles', ('Bertidae 007',)),
    ('Copepods', ('Copepoda 001', 'Copepoda 002')),
    ('Mites', ('Acari',)),
    ('Unidentified arachnids', ('Arachnida',)),
    ('Caterpillars', ('Lepidoptera immatures',)),
    ('Nematodes', ('Nematoda',)),
    ('Pauropods', ('Pauropoda 001',)),
    ('Proturans', ('Protura 001',)),
    ('Shore flies', ('Ephdyridae 018',)),
    ('Snails & slugs', ('Gastropoda',)),
    ('Springtails', ('Collembola',)),
    ('Thrips', ('Thysanoptera',)),
    ('Earthworms', ('Annelida', 'Earthworms')),
    ('Other arthropods', ('Arthropod eggs', 'incertae sedis')),
)

GROWER_MORPHO_FAMILY_DISPLAY = {
    morpho_name: display_label
    for display_label, morpho_names in GROWER_FAMILY_DISPLAY_GROUPS
    for morpho_name in morpho_names
}

GROWER_FAMILY_DISPLAY_FALLBACK = 'Other'

# grower family labels for Insects results display
GROWER_FAMILY_COMMON_NAME_ALIASES: dict[str, tuple[str, str, str]] = {
    'Mites': ('subclass', 'Acari', 'Acari'),
    'Springtails': ('class', 'Collembola', 'Collembola'),
    'Earthworms': ('class', 'Clitellata', 'Clitellata'),
    'Snails & slugs': ('class', 'Gastropoda', 'Gastropoda'),
    'Thrips': ('order', 'Thysanoptera', 'Thysanoptera'),
    'Unidentified arachnids': ('class', 'Arachnida', 'Unidentified arachnids'),
    'Caterpillars': ('order', 'Lepidoptera', 'Lepidoptera'),
    'Shore flies': ('family', 'Ephydridae', 'Ephydridae'),
}

INSECT_COMMON_NAMES: dict[tuple[str, str], str] = {
    ('class', 'Arachnida'): 'Spiders, mites and scorpions',
    ('class', 'Branchiopoda'): 'Freshwater crustaceans',
    ('class', 'Chilopoda'): 'Centipedes',
    ('class', 'Clitellata'): 'Earthworms',
    ('class', 'Collembola'): 'Springtails',
    ('class', 'Copepoda'): 'Copepods',
    ('class', 'Diplopoda'): 'Millipedes',
    ('class', 'Entognatha'): 'Basal insects',
    ('class', 'Gastropoda'): 'Slugs and snails',
    ('class', 'Insecta'): 'Insects',
    ('class', 'Malacostraca'): 'Terrestrial crustaceans',
    ('class', 'Pauropoda'): 'Pauropods',
    ('class', 'Symphyla'): 'Garden centipedes',
    ('subclass', 'Acari'): 'Mites',
    ('family', 'Acanaloniidae'): 'Acanaloniid planthoppers',
    ('family', 'Acaridae'): 'Mites',
    ('family', 'Achilidae'): 'Achilid planthoppers',
    ('family', 'Aclerdidae'): 'Flat grass scales',
    ('family', 'Acrididae'): 'Short-horned grasshoppers / locusts',
    ('family', 'Aeolothripidae'): 'Predatory thrips / banded thrips',
    ('family', 'Agelenidae'): 'Funnel weavers / grass spiders',
    ('family', 'Agromyzidae'): 'Leafminer flies',
    ('family', 'Aleyrodidae'): 'Whiteflies',
    ('family', 'Alucitidae'): 'Many-plumed moths',
    ('family', 'Alydidae'): 'Broad-headed bugs',
    ('family', 'Amaurobiidae'): 'Tangled nest spiders / hackledmesh weavers',
    ('family', 'Ampedidae'): '',
    ('family', 'Amphipsocidae'): 'Hairy-winged barklice',
    ('family', 'Andrenidae'): 'Mining bees',
    ('family', 'Anisopodidae'): 'Wood gnats',
    ('family', 'Anthicidae'): 'Ant-like flower beetles',
    ('family', 'Anthocoridae'): 'Minute pirate bugs',
    ('family', 'Anthomyiidae'): 'Root-maggot flies',
    ('family', 'Anthomyzidae'): 'Flower flies',
    ('family', 'Anthribidae'): 'Fungus weevils',
    ('family', 'Aphalaridae'): '',
    ('family', 'Aphelinidae'): 'Aphid parasitoid wasps',
    ('family', 'Aphididae'): 'Aphids / plant lice',
    ('family', 'Aphodiidae'): 'Aphodiine dung beetles',
    ('family', 'Aphrophoridae'): 'Spittlebugs / froghoppers',
    ('family', 'Apidae'): 'Honey bees, bumble bees, and carpenter bees',
    ('family', 'Apionidae'): 'Pear-shaped weevils',
    ('family', 'Araneidae'): 'Orb-weaver spiders',
    ('family', 'Argidae'): 'Argid sawflies',
    ('family', 'Armadillidiidae'): 'Pillbugs / roly-polies',
    ('family', 'Arrenuridae'): 'Water mites',
    ('family', 'Asilidae'): 'Robber flies',
    ('family', 'Asteiidae'): '',
    ('family', 'Attevidae'): 'Tropical ermine moths',
    ('family', 'Baetidae'): 'Small minnow mayflies',
    ('family', 'Belostomatidae'): 'Giant water bugs / toe-biters',
    ('family', 'Berytidae'): 'Stilt bugs',
    ('family', 'Bethylidae'): 'Flat wasps',
    ('family', 'Bibionidae'): 'March flies / lovebugs',
    ('family', 'Blastobasidae'): 'Scavenger moths',
    ('family', 'Blattidae'): 'Cockroaches',
    ('family', 'Blissidae'): 'Chinch bugs',
    ('family', 'Bombyliidae'): 'Bee flies',
    ('family', 'Braconidae'): 'Braconid wasps',
    ('family', 'Brentidae'): 'Straight-snouted weevils',
    ('family', 'Buprestidae'): 'Jewel beetles',
    ('family', 'Buthidae'): 'Fat-tailed scorpions',
    ('family', 'Caeciliusidae'): 'Lizard barklice',
    ('family', 'Caliscelidae'): 'Piglet bugs',
    ('family', 'Calliphoridae'): 'Blow flies / bottle flies',
    ('family', 'Calophyidae'): '',
    ('family', 'Calopterygidae'): 'Broad-winged damselflies',
    ('family', 'Camillidae'): '',
    ('family', 'Campodeidae'): 'Two-pronged bristletails',
    ('family', 'Canacidae'): 'Beach flies / surf flies',
    ('family', 'Cantharidae'): 'Soldier beetles',
    ('family', 'Carabidae'): 'Ground beetles',
    ('family', 'Carnidae'): 'Bird flies',
    ('family', 'Carposinidae'): 'Fruitworm moths',
    ('family', 'Cecidomyiidae'): 'Gall midges / gall gnats',
    ('family', 'Cephidae'): 'Stem sawflies',
    ('family', 'Cerambycidae'): 'Longhorned beetles',
    ('family', 'Ceraphronidae'): 'Parasitoid wasps',
    ('family', 'Ceratocombidae'): '',
    ('family', 'Ceratopogonidae'): 'Biting midges / no-see-ums',
    ('family', 'Cercopidae'): 'Froghoppers / spittlebugs',
    ('family', 'Cetoniidae'): 'Fruit chafers / flower chafers',
    ('family', 'Chalcididae'): 'Parasitoid wasps',
    ('family', 'Chamaemyiidae'): 'Aphid-eating flies',
    ('family', 'Chaoboridae'): 'Phantom midges',
    ('family', 'Chironomidae'): 'Non-biting midges',
    ('family', 'Chloropidae'): 'Grass flies / frit flies',
    ('family', 'Chrysididae'): 'Cuckoo wasps',
    ('family', 'Chrysomelidae'): 'Leaf beetles',
    ('family', 'Chrysopidae'): 'Green lacewings',
    ('family', 'Chthoniidae'): '',
    ('family', 'Chyromyidae'): '',
    ('family', 'Cicadellidae'): 'Leafhoppers',
    ('family', 'Cicadidae'): 'Cicadas',
    ('family', 'Cimicidae'): 'Bed bugs',
    ('family', 'Cixiidae'): 'Cixiid planthoppers',
    ('family', 'Clastopteridae'): 'Clastopterid spittlebugs',
    ('family', 'Cleridae'): 'Checkered beetles',
    ('family', 'Clubionidae'): 'Sac spiders',
    ('family', 'Clusiidae'): 'Druid flies',
    ('family', 'Coccidae'): 'Soft scale insects',
    ('family', 'Coccinellidae'): 'Ladybugs / ladybird beetles',
    ('family', 'Coenagrionidae'): 'Narrow-winged damselflies / pond damselflies',
    ('family', 'Coleophoridae'): 'Case-bearer moths',
    ('family', 'Colletidae'): 'Cellophane bees',
    ('family', 'Coniopterygidae'): 'Dusty lacewings',
    ('family', 'Conopidae'): 'Thick-headed flies',
    ('family', 'Coreidae'): 'Leaf-footed bugs / squash bugs',
    ('family', 'Corinnidae'): 'Ant-mimic spiders',
    ('family', 'Corixidae'): 'Water boatmen',
    ('family', 'Corydalidae'): 'Dobsonflies and fishflies',
    ('family', 'Corylophidae'): 'Minute hooded beetles',
    ('family', 'Cosmopterigidae'): 'Cosmet moths',
    ('family', 'Crabronidae'): 'Square-headed wasps / sand wasps',
    ('family', 'Crambidae'): 'Crambid snout moths / webworms',
    ('family', 'Cryptophagidae'): 'Silken fungus beetles',
    ('family', 'Culicidae'): 'Mosquitoes',
    ('family', 'Curculionidae'): 'True weevils / snout beetles',
    ('family', 'Cydnidae'): 'Burrower bugs',
    ('family', 'Cymidae'): 'Cymid seed bugs',
    ('family', 'Cynipidae'): 'Gall wasps',
    ('family', 'Daphniidae'): 'Water fleas',
    ('family', 'Delphacidae'): 'Delphacid planthoppers',
    ('family', 'Derbidae'): 'Derbid planthoppers',
    ('family', 'Dermestidae'): 'Carpet beetles / larder beetles',
    ('family', 'Diapheromeridae'): 'Common walkingsticks',
    ('family', 'Diapriidae'): 'Parasitoid wasps',
    ('family', 'Diastatidae'): '',
    ('family', 'Dictynidae'): 'Meshweb weavers',
    ('family', 'Dictyopharidae'): 'Dictyopharid planthoppers',
    ('family', 'Dolichopodidae'): 'Long-legged flies',
    ('family', 'Drepanidae'): 'Hook-tip moths',
    ('family', 'Drosophilidae'): 'Vinegar flies / pomace flies / fruit flies',
    ('family', 'Dryinidae'): 'Pincer wasps',
    ('family', 'Dryomyzidae'): '',
    ('family', 'Dysderidae'): 'Woodlouse spiders',
    ('family', 'Dytiscidae'): 'Predaceous diving beetles',
    ('family', 'Ectobiidae'): 'Wood roaches',
    ('family', 'Ectopsocidae'): 'Outer barklice',
    ('family', 'Elachistidae'): 'Grass miner moths',
    ('family', 'Elateridae'): 'Click beetles / wireworms',
    ('family', 'Empididae'): 'Dagger flies / dance flies',
    ('family', 'Encyrtidae'): 'Parasitoid wasps',
    ('family', 'Enicocephalidae'): 'Unique-headed bugs / gnat bugs',
    ('family', 'Entomobryidae'): 'Slender springtails',
    ('family', 'Ephemerellidae'): 'Spiny crawler mayflies',
    ('family', 'Ephydridae'): 'Shore flies',
    ('family', 'Erebidae'): 'Erebid moths and tiger moths',
    ('family', 'Eremobatidae'): '',
    ('family', 'Erotylidae'): 'Pleasing fungus beetles',
    ('family', 'Eucharitidae'): 'Parasitoid wasps',
    ('family', 'Eucinetidae'): 'Plate-thigh beetles',
    ('family', 'Eulophidae'): 'Parasitoid wasps',
    ('family', 'Eumenidae'): 'Potter wasps / mason wasps',
    ('family', 'Eupelmidae'): 'Parasitoid wasps',
    ('family', 'Eurytomidae'): 'Seed chalcids',
    ('family', 'Evaniidae'): 'Ensign wasps',
    ('family', 'Fanniidae'): '',
    ('family', 'Figitidae'): 'Parasitoid wasps',
    ('family', 'Flatidae'): '',
    ('family', 'Forficulidae'): 'Common earwigs',
    ('family', 'Formicidae'): 'Ants',
    ('family', 'Fulgoridae'): 'Lanternflies',
    ('family', 'Gelechiidae'): 'Twirler moths',
    ('family', 'Geocoridae'): 'Big-eyed bugs',
    ('family', 'Geometridae'): 'Geometer moths / inchworms',
    ('family', 'Geophilidae'): 'Soil centipedes',
    ('family', 'Geotrupidae'): 'Earth-boring dung beetles',
    ('family', 'Gerridae'): 'Water striders / pond skaters',
    ('family', 'Gnaphosidae'): 'Ground spiders',
    ('family', 'Gracillariidae'): 'Leafminer moths',
    ('family', 'Gryllidae'): 'True crickets',
    ('family', 'Gryllotalpidae'): 'Mole crickets',
    ('family', 'Hahniidae'): 'Dwarf sheet-spider',
    ('family', 'Halictidae'): 'Sweat bees',
    ('family', 'Halictophagidae'): 'Twisted-winged parasites of leafhoppers',
    ('family', 'Haliplidae'): 'Crawling water beetles',
    ('family', 'Heleomyzidae'): 'Spiny-winged flies',
    ('family', 'Helophoridae'): 'Wrinkled bark beetles',
    ('family', 'Heloridae'): 'Parasitoid wasps',
    ('family', 'Hemerobiidae'): 'Brown lacewings',
    ('family', 'Henicopidae'): '',
    ('family', 'Heptageniidae'): 'Flatheaded mayflies',
    ('family', 'Hesperiidae'): 'Skippers',
    ('family', 'Heteroceridae'): 'Variegated mud-loving beetles',
    ('family', 'Heterocheilidae'): '',
    ('family', 'Heterogastridae'): '',
    ('family', 'Heteronemiidae'): '',
    ('family', 'Histeridae'): 'Clown beetles',
    ('family', 'Hybotidae'): 'Dance flies',
    ('family', 'Hydraenidae'): 'Minute moss beetles',
    ('family', 'Hydrophilidae'): 'Water scavenger beetles',
    ('family', 'Hydropsychidae'): 'Net-spinning caddisflies',
    ('family', 'Hydroptilidae'): 'Micro-caddisflies',
    ('family', 'Ichneumonidae'): 'Ichneumon wasps',
    ('family', 'Isotomidae'): 'Smooth springtails',
    ('family', 'Issidae'): 'Issid planthoppers',
    ('family', 'Ixodidae'): 'Ticks',
    ('family', 'Japygidae'): 'Forcepstails',
    ('family', 'Julidae'): 'Snake millipedes',
    ('family', 'Kalotermitidae'): 'Drywood termites',
    ('family', 'Keroplatidae'): 'Predatory fungus gnats',
    ('family', 'Lachesillidae'): 'Fateful barklice',
    ('family', 'Laemophloeidae'): 'Lined flat bark beetles',
    ('family', 'Lampyridae'): 'Fireflies / lightning bugs',
    ('family', 'Largidae'): 'Bordered plant bugs',
    ('family', 'Lasiocampidae'): 'Tent caterpillar moths / lappet moths',
    ('family', 'Latridiidae'): 'Minute scavenger beetles',
    ('family', 'Lauxaniidae'): '',
    ('family', 'Leiodidae'): 'Round fungus beetles',
    ('family', 'Lepismatidae'): 'Silverfish',
    ('family', 'Leptoceridae'): 'Long-horned caddisflies',
    ('family', 'Leptophlebiidae'): 'Prong-gilled mayflies',
    ('family', 'Leptopodidae'): 'Spiny-legged bugs',
    ('family', 'Lestidae'): 'Spread-winged damselflies',
    ('family', 'Libellulidae'): 'Common skimmers',
    ('family', 'Limnephilidae'): 'Northern caddisflies',
    ('family', 'Limoniidae'): 'Limoniid crane flies',
    ('family', 'Linyphiidae'): 'Sheetweaver spiders / money spiders',
    ('family', 'Liposcelididae'): 'Booklice',
    ('family', 'Lithobiidae'): 'Stone centipedes',
    ('family', 'Liviidae'): 'Liviid plantlice',
    ('family', 'Lonchaeidae'): 'Lance flies',
    ('family', 'Lonchopteridae'): 'Spear-winged flies',
    ('family', 'Lycaenidae'): 'Gossamer-winged butterflies',
    ('family', 'Lycidae'): 'Net-winged beetles',
    ('family', 'Lycosidae'): 'Wolf spiders',
    ('family', 'Lygaeidae'): 'Seed bugs',
    ('family', 'Lyonetiidae'): 'Lyonet moths',
    ('family', 'Mantidae'): 'Mantises',
    ('family', 'Mantispidae'): 'Mantisflies',
    ('family', 'Megachilidae'): 'Leafcutter bees / mason bees',
    ('family', 'Megalopygidae'): 'Flannel moths',
    ('family', 'Megaspilidae'): 'Parasitoid wasps',
    ('family', 'Meinertellidae'): 'Rock bristletails',
    ('family', 'Melittidae'): 'Melittid bees',
    ('family', 'Meloidae'): 'Blister beetles',
    ('family', 'Melyridae'): 'Soft-winged flower beetles',
    ('family', 'Membracidae'): 'Treehoppers',
    ('family', 'Mesoveliidae'): 'Water treaders',
    ('family', 'Micropezidae'): 'Stilt-legged flies',
    ('family', 'Microtrombidiidae'): 'Small velvet mites',
    ('family', 'Milichiidae'): 'Freeloader flies',
    ('family', 'Mimetidae'): 'Pirate spiders',
    ('family', 'Miridae'): 'Plant bugs / grass bugs',
    ('family', 'Monotomidae'): 'Root-eating beetles',
    ('family', 'Mordellidae'): 'Tumbling flower beetles',
    ('family', 'Muscidae'): 'House flies / filth flies',
    ('family', 'Mutillidae'): 'Velvet ants',
    ('family', 'Mycetophagidae'): 'Hairy fungus beetles',
    ('family', 'Mycetophilidae'): 'Fungus gnats',
    ('family', 'Mydidae'): 'Mydas flies',
    ('family', 'Mymaridae'): 'Fairyflies / fairy wasps',
    ('family', 'Myrmeleontidae'): 'Antlions',
    ('family', 'Myrmosidae'): 'Bee-parasitoid wasps',
    ('family', 'Mythicomyiidae'): 'Micro-bee flies',
    ('family', 'Nabidae'): 'Damsel bugs',
    ('family', 'Neobisiidae'): '',
    ('family', 'Nepidae'): 'Water scorpions',
    ('family', 'Nepticulidae'): 'Pygmy moths',
    ('family', 'Nitidulidae'): 'Sap beetles',
    ('family', 'Noctuidae'): 'Owlet moths, cutworms and armyworms',
    ('family', 'Nolidae'): 'Tuft moths',
    ('family', 'Notodontidae'): 'Prominents',
    ('family', 'Notonectidae'): 'Backswimmers',
    ('family', 'Nymphalidae'): 'Brush-footed butterflies',
    ('family', 'Oligotomidae'): 'Webspinners',
    ('family', 'Opomyzidae'): 'Opomyzid flies',
    ('family', 'Opostegidae'): '',
    ('family', 'Oxycarenidae'): 'Ground bugs',
    ('family', 'Oxyopidae'): 'Lynx spiders',
    ('family', 'Pachygronthidae'): 'Pachygronthid bugs',
    ('family', 'Pallopteridae'): 'Flutter-winged flies',
    ('family', 'Papilionidae'): 'Swallowtails',
    ('family', 'Paradoxosomatidae'): 'Strong-gilded millipedes',
    ('family', 'Parajapygidae'): 'Forcepstails',
    ('family', 'Parajulidae'): '',
    ('family', 'Parasitidae'): 'Mites',
    ('family', 'Passandridae'): 'Parasitic flat bark beetles',
    ('family', 'Pelecinidae'): '',
    ('family', 'Pemphredonidae'): 'Aphid wasps',
    ('family', 'Pentatomidae'): 'Stink bugs / shield bugs',
    ('family', 'Perilampidae'): 'Parasitoid wasps',
    ('family', 'Peripsocidae'): 'Perimeter barklice',
    ('family', 'Perlidae'): 'Common stoneflies',
    ('family', 'Phalacridae'): 'Shining flower beetles',
    ('family', 'Phalangiidae'): '',
    ('family', 'Philodromidae'): 'Running crab spiders',
    ('family', 'Philosciidae'): 'Philosciid woodlice',
    ('family', 'Philotarsidae'): '',
    ('family', 'Pholcidae'): 'Cellar spiders',
    ('family', 'Phoridae'): 'Scuttle flies / hump-backed flies',
    ('family', 'Phrurolithidae'): 'Guardstone spiders',
    ('family', 'Phryganeidae'): 'Giant caddisflies',
    ('family', 'Pieridae'): 'Whites and yellows / cabbage butterflies',
    ('family', 'Piesmatidae'): 'Ash-gray leaf bugs',
    ('family', 'Piophilidae'): 'Cheese skippers',
    ('family', 'Pipunculidae'): 'Big-headed flies',
    ('family', 'Pirenidae'): '',
    ('family', 'Plataspidae'): 'Kudzu bugs',
    ('family', 'Platygastridae'): 'Parasitoid wasps',
    ('family', 'Platystomatidae'): 'Signal flies',
    ('family', 'Pleidae'): 'Pygmy backswimmers',
    ('family', 'Plutellidae'): 'Diamondback moths',
    ('family', 'Polleniidae'): 'Cluster flies',
    ('family', 'Polydesmidae'): 'Flat-backed millipedes',
    ('family', 'Pompilidae'): 'Spider wasps',
    ('family', 'Porcellionidae'): 'Sowbugs / woodlice',
    ('family', 'Proctotrupidae'): 'Parasitoid wasps',
    ('family', 'Protolophidae'): 'Harvestmen',
    ('family', 'Pseudococcidae'): 'Mealybugs',
    ('family', 'Psilidae'): 'Rust flies',
    ('family', 'Psocidae'): 'Common barklice',
    ('family', 'Psychodidae'): 'Drain flies / moth flies / sand flies',
    ('family', 'Psyllidae'): 'Jumping plant lice / psyllids',
    ('family', 'Pteromalidae'): 'Parasitoid wasps',
    ('family', 'Pterophoridae'): 'Plume moths',
    ('family', 'Ptiliidae'): 'Featherwing beetles',
    ('family', 'Ptinidae'): 'Spider beetles & deathwatch beetles',
    ('family', 'Ptychopteridae'): 'Phantom crane flies',
    ('family', 'Pyralidae'): 'Pyralid snout moths',
    ('family', 'Pyrgotidae'): '',
    ('family', 'Pyrrhocoridae'): 'Red bugs / cotton stainers',
    ('family', 'Raphidiidae'): 'Snakeflies',
    ('family', 'Reduviidae'): 'Assassin bugs',
    ('family', 'Rhagionidae'): 'Snipe flies',
    ('family', 'Rhopalidae'): 'Scentless plant bugs',
    ('family', 'Rhopalosomatidae'): 'Parasitoid wasps',
    ('family', 'Rhyparochromidae'): 'Dirt-colored seed bugs',
    ('family', 'Ripiphoridae'): 'Wedge-shaped beetles',
    ('family', 'Romaleidae'): 'Lubber grasshoppers',
    ('family', 'Saldidae'): 'Shore bugs',
    ('family', 'Salticidae'): 'Jumping spiders',
    ('family', 'Sarcophagidae'): 'Flesh flies',
    ('family', 'Scarabaeidae'): 'Scarab beetles',
    ('family', 'Scathophagidae'): 'Dung flies',
    ('family', 'Scatopsidae'): 'Minute scavenger flies',
    ('family', 'Scelionidae'): 'Parasitoid wasps',
    ('family', 'Scenopinidae'): 'Window flies',
    ('family', 'Schendylidae'): '',
    ('family', 'Sciaridae'): 'Fungus gnats',
    ('family', 'Sciomyzidae'): 'Marsh flies / snail-killing flies',
    ('family', 'Scirtidae'): 'Marsh beetles',
    ('family', 'Sclerosomatidae'): '',
    ('family', 'Scoliidae'): 'Mammoth wasps',
    ('family', 'Scolopendrellidae'): '',
    ('family', 'Scolopendridae'): 'Tropical centipedes',
    ('family', 'Scraptiidae'): 'False flower beetles',
    ('family', 'Scutelleridae'): 'Shield-backed bugs',
    ('family', 'Scutigerellidae'): 'Symphylans / garden centipedes',
    ('family', 'Sepsidae'): 'Black scavenger flies / ensign flies',
    ('family', 'Sierolomorphidae'): 'Parasitoid wasps',
    ('family', 'Signiphoridae'): 'Parasitoid wasps',
    ('family', 'Silvanidae'): 'Silvanid flat bark beetles',
    ('family', 'Simuliidae'): 'Black flies',
    ('family', 'Siricidae'): 'Horntails / wood wasps',
    ('family', 'Sminthuridae'): 'Globular springtails',
    ('family', 'Sphaeroceridae'): 'Lesser dung flies',
    ('family', 'Sphecidae'): 'Thread-waisted wasps',
    ('family', 'Sphingidae'): 'Sphinx moths',
    ('family', 'Spirobolidae'): '',
    ('family', 'Spongiphoridae'): 'Little earwigs',
    ('family', 'Staphylinidae'): 'Rove beetles',
    ('family', 'Stenopelmatidae'): 'Jerusalem crickets',
    ('family', 'Stenopsocidae'): 'Narrow barklice',
    ('family', 'Stratiomyidae'): 'Soldier flies',
    ('family', 'Syrphidae'): 'Hover flies',
    ('family', 'Tabanidae'): 'Deer flies and horse flies',
    ('family', 'Tachinidae'): 'Parasitic flies',
    ('family', 'Tanypezidae'): '',
    ('family', 'Tenebrionidae'): 'Darkling beetles',
    ('family', 'Tenthredinidae'): 'Common sawflies',
    ('family', 'Tephritidae'): 'Fruit flies',
    ('family', 'Termitidae'): 'Common termites',
    ('family', 'Tetragnathidae'): 'Long-jawed orb-weavers',
    ('family', 'Tetrigidae'): 'Pygmy grasshoppers',
    ('family', 'Tettigoniidae'): 'Katydids',
    ('family', 'Therevidae'): 'Stiletto flies',
    ('family', 'Theridiidae'): 'Cobweb spiders',
    ('family', 'Thomisidae'): 'Crab spiders',
    ('family', 'Thripidae'): 'Common thrips',
    ('family', 'Throscidae'): 'False click beetles',
    ('family', 'Thynnidae'): 'Flower wasps',
    ('family', 'Thyreocoridae'): 'Ebony bugs',
    ('family', 'Tineidae'): 'Fungus moths / clothes moths',
    ('family', 'Tingidae'): 'Lace bugs',
    ('family', 'Tiphiidae'): 'Flower wasps',
    ('family', 'Tipulidae'): 'Crane flies',
    ('family', 'Tischeriidae'): 'Trumpet leafminer moths',
    ('family', 'Titanoecidae'): 'Rock weavers',
    ('family', 'Tortricidae'): 'Leafroller moths',
    ('family', 'Torymidae'): 'Parasitoid wasps',
    ('family', 'Trachelidae'): 'Ground sac spiders',
    ('family', 'Trichogrammatidae'): 'Parasitoid wasps',
    ('family', 'Trichoniscidae'): '',
    ('family', 'Trigonalidae'): 'Parasitoid wasps',
    ('family', 'Trigonidiidae'): 'Trigs / ground crickets',
    ('family', 'Triozidae'): 'Triozid plant lice',
    ('family', 'Ulidiidae'): 'Picture-winged flies',
    ('family', 'Vespidae'): 'Hornets, yellowjackets and other stinging wasps',
    ('family', 'Xylomyidae'): 'Wood soldier flies',
    ('family', 'Zodariidae'): 'Ant spiders',
    ('family', 'Zopheridae'): 'Ironclad beetles',
    ('order', 'Anomopoda'): '',
    ('order', 'Araneae'): 'Spiders',
    ('order', 'Astigmata'): '',
    ('order', 'Blattodea'): 'Cockroaches & termites',
    ('order', 'Coleoptera'): 'Beetles',
    ('order', 'Collembola'): 'Springtails',
    ('order', 'Dermaptera'): 'Earwigs',
    ('order', 'Diplura'): 'Two-pronged bristletails',
    ('order', 'Diptera'): 'True flies',
    ('order', 'Embioptera'): 'Webspinners',
    ('order', 'Entomobryomorpha'): 'Elongate springtails',
    ('order', 'Ephemeroptera'): 'Mayflies',
    ('order', 'Geophilomorpha'): 'Soil centipedes',
    ('order', 'Hemiptera'): 'True bugs',
    ('order', 'Hymenoptera'): 'Ants, bees & wasps',
    ('order', 'Isopoda'): 'Isopods / woodlice / pillbugs',
    ('order', 'Ixodida'): 'Ticks',
    ('order', 'Julida'): 'Common millipedes',
    ('order', 'Lepidoptera'): 'Butterflies & moths',
    ('order', 'Lithobiomorpha'): 'Stone centipedes',
    ('order', 'Mantodea'): 'Mantises',
    ('order', 'Mesostigmata'): '',
    ('order', 'Microcoryphia'): 'Bristletails',
    ('order', 'Neuroptera'): 'Antlions & lacewings',
    ('order', 'Odonata'): 'Dragonflies & damselflies',
    ('order', 'Opiliones'): 'Harvestmen / daddy longlegs',
    ('order', 'Orthoptera'): 'Crickets, grasshoppers & katydids',
    ('order', 'Phasmida'): 'Stick insects / walkingsticks',
    ('order', 'Plecoptera'): 'Stoneflies',
    ('order', 'Polydesmida'): 'Flat-backed millipedes',
    ('order', 'Pseudoscorpiones'): 'Pseudoscorpions',
    ('order', 'Psocodea'): 'Lice',
    ('order', 'Raphidioptera'): 'Snakeflies',
    ('order', 'Scorpiones'): 'Scorpions',
    ('order', 'Solifugae'): 'Camel spiders / sun spiders / solifuges',
    ('order', 'Spirobolida'): 'Iron millipedes',
    ('order', 'Strepsiptera'): 'Twisted-winged parasites',
    ('order', 'Symphypleona'): 'Globular spingtails',
    ('order', 'Thysanoptera'): 'Thrips',
    ('order', 'Trichoptera'): 'Caddisflies',
    ('order', 'Trombidiformes'): '',
    ('order', 'Zygentoma'): 'Silverfish',
}

# Morphospecies functional group.. insects results
GROWER_FUNCTIONAL_GROUP_CATEGORIES = (
    {'key': 'herbivore', 'label': 'Herbivores', 'color': '#2e7d32'},
    {'key': 'natural_enemy', 'label': 'Natural enemies', 'color': '#e91e8c'},
    {'key': 'detritivore', 'label': 'Recyclers', 'color': '#795548'},
    {'key': 'pollinator', 'label': 'Pollinators', 'color': '#f9a825'},
)
