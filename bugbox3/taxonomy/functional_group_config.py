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
    'Parent = how much the species fits that feeding group (Zoophagous or Phytophagous). '
    'Subtype = how it feeds. Weights are 0 to 1.'
)

# (title, body paragraphs as plain strings; HTML allowed only as &lt; for <)
FUNCTIONAL_GROUP_WEIGHT_GUIDE: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        'Parent = 1, subtype = 1',
        (
            'Fully in that group. Example: zoophagous = 1 and predator = 1 = pure predator. '
            'Use the single feeding type dropdown. You must set the parent if you set a subtype.',
        ),
    ),
    (
        'Parent = 1, fractional subtypes',
        (
            'Fully in that group, but more than one feeding mode. '
            'Example: phytophagous = 1, phyllophagous = 0.5, stem-feeding = 0.5 (leaves + stems). '
            'Fractions must sum to 1.',
        ),
    ),
    (
        'Parent &lt; 1 (e.g. 0.5)',
        (
            'Only partly in that group, often a mixed diet. '
            'Example: phytophagous = 0.5, zoophagous = 0.5, predator = 1 = herbivore and predator. '
            'Subtype = 1 means the feeding mode, not half a predator.',
        ),
    ),
)

PARENT_SUBTYPE_SECTION_HELP: dict[str, str] = {
    'zoophagous': (
        'Set Zoophagous (overall) for how animal-focused this species is. '
        'Set a subtype (predator, parasitoid, …) for how it feeds on animals. '
        'Predator = 1 alone is invalid; zoophagous must also be set (usually 1 for a pure predator).'
    ),
    'phytophagous': (
        'Set Phytophagous (overall) for how plant-focused this species is. '
        'Set a subtype (leaves, sap, roots, …) for feeding mode. '
        'A subtype alone without phytophagous is invalid.'
    ),
}

OTHER_SECTION_HELP = (
    'Check any additional roles. Each applies at weight 1 (detritivore, pollinator, fungivore, etc.).'
)

LIFE_STAGE_FORM_HELP = (
    'Each selection is saved as weight 1 (habitat metadata). '
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
