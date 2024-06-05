from django.db.models.fields import BLANK_CHOICE_DASH

FIELD_MORPHO_NAME = 'name'
FIELD_MORPHO_DEFUNT_DATE = 'defunt_date'
FIELD_MORPHO_GBIF_KEY = 'gbif_key'
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
FIELD_MORPHO_BYPASS = 'bypass'
FIELD_MORPHO_DATE_ADDED = 'date_added'
FIELD_MORPHO_DATE_MODIFIED = 'date_modified'
FIELD_MORPHO_NOTE = 'note'

GBIF_RANK_KINGDOM = 'kingdom'
GBIF_RANK_ORDER = 'order'
GBIF_RANK_FAMILY = 'family'
GBIF_RANK_GENUS = 'genus'
GBIF_RANK_SPECIES = 'species'

GBIF_RANK_CHOICES = (
    BLANK_CHOICE_DASH[0],
    (GBIF_RANK_KINGDOM, GBIF_RANK_KINGDOM),
    (GBIF_RANK_ORDER, GBIF_RANK_ORDER),
    (GBIF_RANK_FAMILY, GBIF_RANK_FAMILY),
    (GBIF_RANK_GENUS, GBIF_RANK_GENUS),
    (GBIF_RANK_SPECIES, GBIF_RANK_SPECIES),
)

GBIF_RANK_CHOICES_WO_BLANK = (v for v in GBIF_RANK_CHOICES if v != BLANK_CHOICE_DASH[0])
GBIF_RANK_CHOICES_WO_BLANK_LIST = [[v[0], v[1]] for v in GBIF_RANK_CHOICES if v != BLANK_CHOICE_DASH[0]]
GBIF_RANK_VALUES = [v[0] for v in GBIF_RANK_CHOICES]

#  Permissions

PERMISSION_MORPHOSPECIES_FUNCTIONS = 'use_morphospecies_functions'
PERMISSION_MORPHOSPECIES_FUNCTIONS_TXT = 'Can use the “Merge” button, ' \
                                         'check the “Bypass” box or change the percent threshold'
