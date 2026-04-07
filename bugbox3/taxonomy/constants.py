from django.db.models.fields import BLANK_CHOICE_DASH

FIELD_MORPHO_ID = 'id'
FIELD_MORPHO_NAME = 'name'
FIELD_MORPHO_DEFUNT_DATE = 'defunt_date'
FIELD_MORPHO_GBIF_KEY = 'gbif_key'
FIELD_MORPHO_GBIF_PHYLUM = 'gbif_phylum'
FIELD_MORPHO_GBIF_CLASS = 'gbif_class'
FIELD_MORPHO_GBIF_ORDER = 'gbif_order'
FIELD_MORPHO_GBIF_FAMILY = 'gbif_family'
FIELD_MORPHO_SUBFAMILY = 'subfamily'
FIELD_MORPHO_GBIF_GENUS = 'gbif_genus'
FIELD_MORPHO_GBIF_SPECIES = 'gbif_species'
FIELD_MORPHO_GBIF_SCIENTIFIC_NAME = 'gbif_scientific_name'
FIELD_MORPHO_GBIF_CANONICAL_NAME = 'gbif_canonical_name'
FIELD_MORPHO_GBIF_RANK = 'gbif_rank'
FIELD_MORPHO_GBIF_STATUS = 'gbif_status'
FIELD_MORPHO_DATE_ADDED = 'date_added'
FIELD_MORPHO_DATE_MODIFIED = 'date_modified'
FIELD_MORPHO_NOTE = 'note'
FIELD_MORPHO_IMAGE = 'image'
FIELD_MORPHO_EXCLUDE = 'exclude_from_export'
FIELD_MORPHO_TAGS = 'tags'
FIELD_MORPHO_TAGS_LOOKUP = 'morpho_tags'
FIELD_MORPHO_FUNCTIONAL_GROUPS = 'functional_groups'
FIELD_MORPHO_TAXONOMY_REVIEWED = 'taxonomy_reviewed'

GROUP_NAME_TAXONOMY_REVIEWER = 'taxonomy_reviewer'

MORPHOSPECIES_TAXONOMY_REVIEW_FIELDS = (
    FIELD_MORPHO_GBIF_KEY,
    FIELD_MORPHO_GBIF_PHYLUM,
    FIELD_MORPHO_GBIF_CLASS,
    FIELD_MORPHO_GBIF_ORDER,
    FIELD_MORPHO_GBIF_FAMILY,
    FIELD_MORPHO_SUBFAMILY,
    FIELD_MORPHO_GBIF_GENUS,
    FIELD_MORPHO_GBIF_SPECIES,
    FIELD_MORPHO_GBIF_SCIENTIFIC_NAME,
    FIELD_MORPHO_GBIF_CANONICAL_NAME,
    FIELD_MORPHO_GBIF_RANK,
    FIELD_MORPHO_GBIF_STATUS,
)

MORPHPOSPECIES_THUMBSIZE = 350

# Form fields

FORM_FIELDS_MORPHO = (
    FIELD_MORPHO_NAME,
    FIELD_MORPHO_GBIF_KEY,
    FIELD_MORPHO_GBIF_PHYLUM,
    FIELD_MORPHO_GBIF_CLASS,
    FIELD_MORPHO_GBIF_ORDER,
    FIELD_MORPHO_GBIF_FAMILY,
    FIELD_MORPHO_SUBFAMILY,
    FIELD_MORPHO_GBIF_GENUS,
    FIELD_MORPHO_GBIF_SPECIES,
    FIELD_MORPHO_GBIF_SCIENTIFIC_NAME,
    FIELD_MORPHO_GBIF_CANONICAL_NAME,
    FIELD_MORPHO_GBIF_RANK,
    FIELD_MORPHO_GBIF_STATUS,
    FIELD_MORPHO_NOTE,
    FIELD_MORPHO_IMAGE,
    FIELD_MORPHO_EXCLUDE,
    FIELD_MORPHO_TAGS,
)

FORM_FIELDS_MORPHO_HIDDEN = (
    FIELD_MORPHO_GBIF_KEY,
    FIELD_MORPHO_GBIF_PHYLUM,
    FIELD_MORPHO_GBIF_CLASS,
    FIELD_MORPHO_GBIF_ORDER,
    FIELD_MORPHO_GBIF_FAMILY,
    FIELD_MORPHO_SUBFAMILY,
    FIELD_MORPHO_GBIF_GENUS,
    FIELD_MORPHO_GBIF_SPECIES,
    FIELD_MORPHO_GBIF_SCIENTIFIC_NAME,
    FIELD_MORPHO_GBIF_RANK,
    FIELD_MORPHO_GBIF_STATUS,
)

FORM_FIELDS_MORPHO_UPDATE_HIDDEN = (
    FIELD_MORPHO_GBIF_KEY,
)

FORM_FIELDS_MORPHO_REQUIRED = (
    FIELD_MORPHO_NAME,
    FIELD_MORPHO_GBIF_KEY,
    FIELD_MORPHO_GBIF_CANONICAL_NAME
)

# Field Labels

FORM_FIELDS_MORPHO_LABELS = {
    FIELD_MORPHO_NAME: 'Name',
    FIELD_MORPHO_GBIF_PHYLUM: 'Phylum',
    FIELD_MORPHO_GBIF_CLASS: 'Class',
    FIELD_MORPHO_GBIF_ORDER: 'Order',
    FIELD_MORPHO_GBIF_FAMILY: 'Family',
    FIELD_MORPHO_SUBFAMILY: 'Subfamily',
    FIELD_MORPHO_GBIF_GENUS: 'Genus',
    FIELD_MORPHO_GBIF_SPECIES: 'Species',
    FIELD_MORPHO_GBIF_SCIENTIFIC_NAME: 'Scientific name',
    FIELD_MORPHO_GBIF_CANONICAL_NAME: 'Canonical name',
    FIELD_MORPHO_GBIF_RANK: 'Rank',
    FIELD_MORPHO_GBIF_STATUS: 'Status',
    FIELD_MORPHO_NOTE: 'Note',
    FIELD_MORPHO_EXCLUDE: 'Exclude from export',
    FIELD_MORPHO_TAGS: 'Tags',
    FIELD_MORPHO_TAXONOMY_REVIEWED: 'Reviewed',
}

# HELP TEXT

FORM_MORPHO_HELP_TEXT = {
    FIELD_MORPHO_NAME: 'Name must be unique',
    FIELD_MORPHO_GBIF_CANONICAL_NAME: 'Populate by selecting a GBIF taxon.'
}

# Functional groups (category codes)
CAT_LIFE_STAGE_YOUNG = 'life_stage_young'
CAT_LIFE_STAGE_ADULT = 'life_stage_adult'
CAT_PHYTOPHAGOUS = 'phytophagous'
CAT_ZOOPHAGOUS = 'zoophagous'
CAT_OTHER = 'other'

# tuple of(code, display_name, description, category)
FUNCTIONAL_GROUP_DEFINITIONS = (
    (
        'young_terrestrial',
        'Young Terrestrial',
        'The immature stages live primarily out of the water',
        CAT_LIFE_STAGE_YOUNG,
    ),
    (
        'young_aquatic',
        'Young Aquatic',
        'The immature stages live primarily in or on the water',
        CAT_LIFE_STAGE_YOUNG,
    ),
    (
        'adult_terrestrial',
        'Adult Terrestrial',
        'The adult stage (imago) lives primarily out of the water',
        CAT_LIFE_STAGE_ADULT,
    ),
    (
        'adult_aquatic',
        'Adult Aquatic',
        'The adult stage (imago) lives primarily in or on the water',
        CAT_LIFE_STAGE_ADULT,
    ),
    (
        'phytophagous',
        'Phytophagous',
        'The species consumes plants (choose all applicable subtypes from the options below)',
        CAT_PHYTOPHAGOUS,
    ),
    (
        'phyllophagous',
        'Phyllophagous',
        'The species consumes the leaves of plants',
        CAT_PHYTOPHAGOUS,
    ),
    (
        'saproxylic',
        'Saproxylic',
        'The species consumes living wood',
        CAT_PHYTOPHAGOUS,
    ),
    (
        'sap_sucking',
        'Sap-sucking',
        'The species consumes liquids from the xylem or phloem of plants',
        CAT_PHYTOPHAGOUS,
    ),
    (
        'stem_feeding',
        'Stem-feeding',
        'The species consumes stem tissues of plants',
        CAT_PHYTOPHAGOUS,
    ),
    (
        'flower_feeding',
        'Flower-feeding',
        'The species consumes flowers or flower parts',
        CAT_PHYTOPHAGOUS,
    ),
    (
        'fruit_seed_feeding',
        'Fruit/seed-feeding',
        'The species consumes fruit and/or seeds',
        CAT_PHYTOPHAGOUS,
    ),
    (
        'gall_inducing',
        'Gall-inducing',
        'The species causes plant tissues to develop a gall, which it lives in and feeds on',
        CAT_PHYTOPHAGOUS,
    ),
    (
        'leaf_miners',
        'Leaf miners',
        "The species' larva lives within leaf tissue and consumes it from within",
        CAT_PHYTOPHAGOUS,
    ),
    (
        'root_feeding',
        'Root-feeding',
        'The species consumes plant roots',
        CAT_PHYTOPHAGOUS,
    ),
    (
        'algae_moss_feeding',
        'Algae/moss-feeding',
        'The species consumes algae or moss',
        CAT_PHYTOPHAGOUS,
    ),
    (
        'zoophagous',
        'Zoophagous',
        'The species consumes other animals (choose all applicable subtypes from the options below)',
        CAT_ZOOPHAGOUS,
    ),
    (
        'predator',
        'Predator',
        'The species kills and consumes animal prey',
        CAT_ZOOPHAGOUS,
    ),
    (
        'micropredator',
        'Micropredator',
        'The species is free-living (i.e., not parasitic), but feeds on body fluids'
        ' or body parts of animals without killing them',
        CAT_ZOOPHAGOUS,
    ),
    (
        'parasite',
        'Parasite',
        "The species lives on or inside a host animal's body and feeds on it, but does not kill it",
        CAT_ZOOPHAGOUS,
    ),
    (
        'parasitoid',
        'Parasitoid',
        'The species lives on or inside a host animal and consumes it, ultimately killing it',
        CAT_ZOOPHAGOUS,
    ),
    (
        'necrophagous',
        'Necrophagous',
        'The species consumes dead animals that it did not kill',
        CAT_ZOOPHAGOUS,
    ),
    (
        'mycetophagous',
        'Mycetophagous',
        'The species consumes fungi',
        CAT_OTHER,
    ),
    (
        'detritophagous',
        'Detritophagous',
        'The species consumes dead/decaying organic matter',
        CAT_OTHER,
    ),
    (
        'coprophagous',
        'Coprophagous',
        'The species consumes dung',
        CAT_OTHER,
    ),
    (
        'pollinator',
        'Pollinator',
        'The species transfers pollen between flowers',
        CAT_OTHER,
    ),
)

PHYTOPHAGOUS_ORDER = [
    'phytophagous', 'phyllophagous', 'saproxylic', 'sap_sucking', 'stem_feeding',
    'flower_feeding', 'fruit_seed_feeding', 'gall_inducing', 'leaf_miners',
    'root_feeding', 'algae_moss_feeding',
]
ZOOPHAGOUS_ORDER = [
    'zoophagous', 'predator', 'micropredator', 'parasite', 'parasitoid', 'necrophagous',
]
OTHER_ORDER = ['mycetophagous', 'detritophagous', 'coprophagous', 'pollinator']

YOUNG_HABITAT_CHOICES = (
    ('', '---------'),
    ('young_terrestrial', 'Young Terrestrial'),
    ('young_aquatic', 'Young Aquatic'),
)

ADULT_HABITAT_CHOICES = (
    ('', '---------'),
    ('adult_terrestrial', 'Adult Terrestrial'),
    ('adult_aquatic', 'Adult Aquatic'),
)

# Choices

GBIF_RANK_KINGDOM = 'KINGDOM'
GBIF_RANK_PHYLUM = 'PHYLUM'
GBIF_RANK_CLASS = 'CLASS'
GBIF_RANK_ORDER = 'ORDER'
GBIF_RANK_FAMILY = 'FAMILY'
GBIF_RANK_GENUS = 'GENUS'
GBIF_RANK_SPECIES = 'SPECIES'

GBIF_RANK_CHOICES = (
    BLANK_CHOICE_DASH[0],
    (GBIF_RANK_KINGDOM, GBIF_RANK_KINGDOM),
    (GBIF_RANK_PHYLUM, GBIF_RANK_PHYLUM),
    (GBIF_RANK_CLASS, GBIF_RANK_CLASS),
    (GBIF_RANK_ORDER, GBIF_RANK_ORDER),
    (GBIF_RANK_FAMILY, GBIF_RANK_FAMILY),
    (GBIF_RANK_GENUS, GBIF_RANK_GENUS),
    (GBIF_RANK_SPECIES, GBIF_RANK_SPECIES),
)

GBIF_RANK_CHOICES_WO_BLANK = [v for v in GBIF_RANK_CHOICES if v != BLANK_CHOICE_DASH[0]]
GBIF_RANK_CHOICES_WO_BLANK_LIST = [[v[0], v[1]] for v in GBIF_RANK_CHOICES if v != BLANK_CHOICE_DASH[0]]
GBIF_RANK_VALUES = [v[0] for v in GBIF_RANK_CHOICES]

# EXPORT LIST

EXPORT_TITLE_TRAINING_SELECTIONS = 'training_selections_csv'

EXPORT_HEADERS_MORPHOSPECIES = [
    FIELD_MORPHO_ID,
    FIELD_MORPHO_NAME,
    FIELD_MORPHO_DEFUNT_DATE,
    FIELD_MORPHO_GBIF_KEY,
    FIELD_MORPHO_GBIF_PHYLUM,
    FIELD_MORPHO_GBIF_CLASS,
    FIELD_MORPHO_GBIF_ORDER,
    FIELD_MORPHO_GBIF_FAMILY,
    FIELD_MORPHO_SUBFAMILY,
    FIELD_MORPHO_GBIF_GENUS,
    FIELD_MORPHO_GBIF_SPECIES,
    FIELD_MORPHO_GBIF_SCIENTIFIC_NAME,
    FIELD_MORPHO_GBIF_CANONICAL_NAME,
    FIELD_MORPHO_GBIF_RANK,
    FIELD_MORPHO_GBIF_STATUS,
    FIELD_MORPHO_DATE_ADDED,
    FIELD_MORPHO_DATE_MODIFIED,
    FIELD_MORPHO_NOTE,
    FIELD_MORPHO_IMAGE,
]

EXP_MORPH_ALL_MORPH = 'all-morph'
EXP_MORPH_CHOICES = ((EXP_MORPH_ALL_MORPH, 'All Morhpospecies'),)
EXP_MORPH_CHOICES_NAMES = [v[0] for v in EXP_MORPH_CHOICES]

# SKIP_MORPHOSPECIES
SKIP_MORPHO_ANNELIDA = 'Annelida'
SKIP_MORPHO_ARACHNIDA = 'Arachnida'
SKIP_MORPHO_COLLEMBOLA = 'Collembola'
SKIP_MORPHO_GASTROPODA = 'Gastropoda'
SKIP_MORPHO_NEMATODA = 'Nematoda'
SKIP_MORPHO_THYSANOPTERA = 'Thysanoptera'
SKIP_RANK_FIELD = 'SKIP_RANK_FIELD'

SKIP_MORPHOSPECIES = (
    {
        FIELD_MORPHO_GBIF_RANK: GBIF_RANK_PHYLUM,
        FIELD_MORPHO_NAME: SKIP_MORPHO_ANNELIDA,
        SKIP_RANK_FIELD: FIELD_MORPHO_GBIF_PHYLUM,
        FIELD_MORPHO_GBIF_PHYLUM: SKIP_MORPHO_ANNELIDA
    },
    {
        FIELD_MORPHO_GBIF_RANK: GBIF_RANK_CLASS,
        FIELD_MORPHO_NAME: SKIP_MORPHO_COLLEMBOLA,
        SKIP_RANK_FIELD: FIELD_MORPHO_GBIF_CLASS,
        FIELD_MORPHO_GBIF_CLASS: SKIP_MORPHO_COLLEMBOLA
    },
    {
        FIELD_MORPHO_GBIF_RANK: GBIF_RANK_CLASS,
        FIELD_MORPHO_NAME: SKIP_MORPHO_GASTROPODA,
        SKIP_RANK_FIELD: FIELD_MORPHO_GBIF_CLASS,
        FIELD_MORPHO_GBIF_CLASS: SKIP_MORPHO_GASTROPODA
    },
    {
        FIELD_MORPHO_GBIF_RANK: GBIF_RANK_PHYLUM,
        FIELD_MORPHO_NAME: SKIP_MORPHO_NEMATODA,
        SKIP_RANK_FIELD: FIELD_MORPHO_GBIF_PHYLUM,
        FIELD_MORPHO_GBIF_PHYLUM: SKIP_MORPHO_NEMATODA
    },
    {
        FIELD_MORPHO_GBIF_RANK: GBIF_RANK_ORDER,
        FIELD_MORPHO_NAME: SKIP_MORPHO_THYSANOPTERA,
        SKIP_RANK_FIELD: FIELD_MORPHO_GBIF_ORDER,
        FIELD_MORPHO_GBIF_ORDER: SKIP_MORPHO_THYSANOPTERA
    },
)
