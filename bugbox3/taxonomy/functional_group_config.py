"""Functional-group UI layout, trait groupings, and form copy"""

from __future__ import annotations

from bugbox3.taxonomy.constants import (
    CAT_LIFE_STAGE_ADULT,
    CAT_LIFE_STAGE_YOUNG,
    CAT_OTHER,
    CAT_PHYTOPHAGOUS,
    CAT_ZOOPHAGOUS,
    OTHER_ORDER,
    PHYTOPHAGOUS_ORDER,
    ZOOPHAGOUS_ORDER,
)

LIFE_STAGE_CODES = ('young_terrestrial', 'young_aquatic', 'adult_terrestrial', 'adult_aquatic')

ZOOPHAGOUS_PARENT_CODE = 'zoophagous'
ZOOPHAGOUS_SUBTYPE_CODES = tuple(
    code for code in ZOOPHAGOUS_ORDER if code != ZOOPHAGOUS_PARENT_CODE
)

PHYTOPHAGOUS_PARENT_CODE = 'phytophagous'
PHYTOPHAGOUS_SUBTYPE_CODES = tuple(
    code for code in PHYTOPHAGOUS_ORDER if code != PHYTOPHAGOUS_PARENT_CODE
)

OTHER_TRAIT_CODES = tuple(OTHER_ORDER)

FUNCTIONAL_GROUP_FORM_INTRO = (
    'Check all feeding roles that apply to this morphospecies.'
)

GROWER_ECOLOGICAL_ROLE_HELP = (
    'Grower portal charts use the ecological roles below. '
    'When multiple roles apply to a morphospecies, the chart splits evenly across those roles.'
)

GROWER_ECOLOGICAL_ROLE_MAPPING: tuple[tuple[str, str], ...] = (
    ('Herbivore', 'phytophagous'),
    ('Natural enemy', 'predator and/or parasitoid'),
    (
        'Detritivore',
        'detritophagous and/or mycetophagous and/or coprophagous and/or necrophagous',
    ),
    ('Pollinator', 'pollinator'),
)

PARENT_SUBTYPE_SECTION_HELP: dict[str, str] = {
    'zoophagous': (
        'Check Zoophagous for general animal feeding, and/or specific modes below '
        '(predator, parasitoid, etc.).'
    ),
    'phytophagous': (
        'Check Phytophagous for general plant feeding, and/or specific modes below '
        '(leaves, sap, roots, etc.).'
    ),
}

OTHER_SECTION_HELP = (
    'Check any additional roles (detritivore, pollinator, fungivore, etc.).'
)

LIFE_STAGE_FORM_HELP = (
    'Habitat metadata for young and adult life stages. '
    'Life stage does not affect grower ecological roles (herbivore, natural enemy, etc.).'
)

FUNCTIONAL_GROUP_UI_SECTIONS: tuple[dict, ...] = (
    {
        'key': 'zoophagous',
        'title': 'Zoophagous',
        'parent_code': ZOOPHAGOUS_PARENT_CODE,
        'subtype_codes': ZOOPHAGOUS_SUBTYPE_CODES,
        'category': CAT_ZOOPHAGOUS,
    },
    {
        'key': 'phytophagous',
        'title': 'Phytophagous',
        'parent_code': PHYTOPHAGOUS_PARENT_CODE,
        'subtype_codes': PHYTOPHAGOUS_SUBTYPE_CODES,
        'category': CAT_PHYTOPHAGOUS,
    },
    {
        'key': 'life_stage',
        'title': 'Life stage',
        'parent_code': None,
        'subtype_codes': LIFE_STAGE_CODES,
        'category': None,
    },
    {
        'key': 'other',
        'title': 'Other',
        'parent_code': None,
        'subtype_codes': OTHER_TRAIT_CODES,
        'category': CAT_OTHER,
    },
)

ALL_TRAIT_CODES: tuple[str, ...] = (
    *LIFE_STAGE_CODES,
    ZOOPHAGOUS_PARENT_CODE,
    *ZOOPHAGOUS_SUBTYPE_CODES,
    PHYTOPHAGOUS_PARENT_CODE,
    *PHYTOPHAGOUS_SUBTYPE_CODES,
    *OTHER_TRAIT_CODES,
)
