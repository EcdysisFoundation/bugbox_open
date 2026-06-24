"""Validation for morphospecies functional-group weights"""

from __future__ import annotations

from django.core.exceptions import ValidationError

from bugbox3.taxonomy.functional_group_config import (
    PHYTOPHAGOUS_PARENT_CODE,
    PHYTOPHAGOUS_SUBTYPE_CODES,
    ZOOPHAGOUS_PARENT_CODE,
    ZOOPHAGOUS_SUBTYPE_CODES,
)

WEIGHT_TOLERANCE = 0.01


def _positive_weights(weights: dict[str, float], codes: tuple[str, ...]) -> dict[str, float]:
    return {code: weights[code] for code in codes if weights.get(code, 0) > 0}


def _is_one(weight: float) -> bool:
    return abs(weight - 1.0) <= WEIGHT_TOLERANCE


def _validate_parent_subtype_group(
    *,
    parent_code: str,
    subtype_codes: tuple[str, ...],
    weights: dict[str, float],
    group_label: str,
) -> None:
    parent = weights.get(parent_code, 0) or 0
    subtypes = _positive_weights(weights, subtype_codes)
    if parent <= 0 and subtypes:
        raise ValidationError(
            f'{group_label}: subtypes are set but {parent_code} is not set.'
        )
    if parent <= 0 or not subtypes:
        return

    has_one = any(_is_one(value) for value in subtypes.values())
    has_fraction = any(not _is_one(value) for value in subtypes.values())
    if has_one and has_fraction:
        raise ValidationError(
            f'{group_label}: do not mix subtype weight 1 with fractional subtype weights.'
        )

    if _is_one(parent) and has_fraction:
        total = sum(subtypes.values())
        if abs(total - 1.0) > WEIGHT_TOLERANCE:
            raise ValidationError(
                f'{group_label}: when {parent_code} is 1 and subtypes use fractions, '
                f'subtype weights must sum to 1 (currently {total:.4f}).'
            )


def validate_phytophagous_group(weights: dict[str, float]) -> None:
    _validate_parent_subtype_group(
        parent_code=PHYTOPHAGOUS_PARENT_CODE,
        subtype_codes=PHYTOPHAGOUS_SUBTYPE_CODES,
        weights=weights,
        group_label='Phytophagous',
    )


def validate_zoophagous_group(weights: dict[str, float]) -> None:
    _validate_parent_subtype_group(
        parent_code=ZOOPHAGOUS_PARENT_CODE,
        subtype_codes=ZOOPHAGOUS_SUBTYPE_CODES,
        weights=weights,
        group_label='Zoophagous',
    )


def _allows_semiterrestrial(habitats: dict[str, float]) -> bool:
    """Kelton CSV uses terrestrial+aquatic both at 1 for semiterrestrial taxa."""
    return len(habitats) == 2 and all(_is_one(value) for value in habitats.values())


def validate_life_stage(weights: dict[str, float]) -> None:
    young = _positive_weights(weights, ('young_terrestrial', 'young_aquatic'))
    adult = _positive_weights(weights, ('adult_terrestrial', 'adult_aquatic'))
    if len(young) > 1 and not _allows_semiterrestrial(young):
        raise ValidationError('Life stage: only one young habitat may be set.')
    if len(adult) > 1 and not _allows_semiterrestrial(adult):
        raise ValidationError('Life stage: only one adult habitat may be set.')


def infer_missing_parent_weights(weights: dict[str, float]) -> dict[str, float]:
    """Default parent to 1 when subtypes are set but parent was left empty."""
    result = dict(weights)
    for parent_code, subtype_codes in (
        (ZOOPHAGOUS_PARENT_CODE, ZOOPHAGOUS_SUBTYPE_CODES),
        (PHYTOPHAGOUS_PARENT_CODE, PHYTOPHAGOUS_SUBTYPE_CODES),
    ):
        if (result.get(parent_code) or 0) > 0:
            continue
        if any((result.get(code) or 0) > 0 for code in subtype_codes):
            result[parent_code] = 1.0
    return result


def validate_functional_group_weights(weights: dict[str, float]) -> None:
    validate_phytophagous_group(weights)
    validate_zoophagous_group(weights)
    validate_life_stage(weights)


def parse_weight_field(value) -> float:
    if value in (None, ''):
        return 0.0
    try:
        weight = float(value)
    except (TypeError, ValueError) as exc:
        raise ValidationError('Enter a valid number between 0 and 1.') from exc
    if weight < 0 or weight > 1:
        raise ValidationError('Weight must be between 0 and 1.')
    return weight
