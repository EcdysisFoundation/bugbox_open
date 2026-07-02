"""Validation for morphospecies functional-group traits"""

from __future__ import annotations

from django.core.exceptions import ValidationError

from bugbox3.taxonomy.functional_group_config import (
    PHYTOPHAGOUS_PARENT_CODE,
    PHYTOPHAGOUS_SUBTYPE_CODES,
    ZOOPHAGOUS_PARENT_CODE,
    ZOOPHAGOUS_SUBTYPE_CODES,
)


def _active_traits(traits: dict[str, bool], codes: tuple[str, ...]) -> dict[str, bool]:
    return {code: True for code in codes if traits.get(code)}


def infer_missing_parent_traits(traits: dict[str, bool]) -> dict[str, bool]:
    result = dict(traits)
    for parent_code, subtype_codes in (
        (ZOOPHAGOUS_PARENT_CODE, ZOOPHAGOUS_SUBTYPE_CODES),
        (PHYTOPHAGOUS_PARENT_CODE, PHYTOPHAGOUS_SUBTYPE_CODES),
    ):
        if result.get(parent_code):
            continue
        if any(result.get(code) for code in subtype_codes):
            result[parent_code] = True
    return result


def validate_life_stage_traits(traits: dict[str, bool]) -> None:
    young = _active_traits(traits, ('young_terrestrial', 'young_aquatic'))
    adult = _active_traits(traits, ('adult_terrestrial', 'adult_aquatic'))
    semiterrestrial_young = len(young) == 2
    semiterrestrial_adult = len(adult) == 2
    if len(young) > 1 and not semiterrestrial_young:
        raise ValidationError('Life stage: only one young habitat may be set.')
    if len(adult) > 1 and not semiterrestrial_adult:
        raise ValidationError('Life stage: only one adult habitat may be set.')


def validate_functional_group_traits(traits: dict[str, bool]) -> None:
    validate_life_stage_traits(traits)
