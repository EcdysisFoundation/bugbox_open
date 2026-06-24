"""Load and save morphospecies functional-group weights"""

from __future__ import annotations

from django.core.exceptions import ValidationError

from bugbox3.taxonomy.functional_group_config import ALL_TRAIT_CODES, FUNCTIONAL_GROUP_UI_SECTIONS
from bugbox3.taxonomy.functional_group_validation import validate_functional_group_weights
from bugbox3.taxonomy.models import FunctionalGroup, Morphospecies, MorphospeciesFunctionalGroup


def get_trait_weights_for_morphospecies(morphospecies: Morphospecies) -> dict[str, float]:
    rows = (
        MorphospeciesFunctionalGroup.objects.filter(morphospecies=morphospecies)
        .select_related('functional_group')
    )
    return {row.functional_group.code: row.weight for row in rows if row.weight > 0}


def get_trait_weights_for_morphospecies_ids(
    morphospecies_ids: set[int] | list[int],
) -> dict[int, dict[str, float]]:
    if not morphospecies_ids:
        return {}
    result: dict[int, dict[str, float]] = {}
    rows = (
        MorphospeciesFunctionalGroup.objects.filter(morphospecies_id__in=morphospecies_ids)
        .select_related('functional_group')
    )
    for row in rows:
        if row.weight <= 0:
            continue
        result.setdefault(row.morphospecies_id, {})[row.functional_group.code] = row.weight
    return result


def set_trait_weights_for_morphospecies(
    morphospecies: Morphospecies,
    weights: dict[str, float],
    *,
    validate: bool = True,
) -> None:
    cleaned = {
        code: float(weight)
        for code, weight in weights.items()
        if code in ALL_TRAIT_CODES and float(weight) > 0
    }
    if validate:
        validate_functional_group_weights(cleaned)

    code_to_fg = {
        fg.code: fg
        for fg in FunctionalGroup.objects.filter(code__in=cleaned.keys())
    }
    missing = sorted(set(cleaned) - set(code_to_fg))
    if missing:
        raise ValidationError(f'Unknown functional group codes: {", ".join(missing)}')

    MorphospeciesFunctionalGroup.objects.filter(morphospecies=morphospecies).delete()
    MorphospeciesFunctionalGroup.objects.bulk_create(
        [
            MorphospeciesFunctionalGroup(
                morphospecies=morphospecies,
                functional_group=code_to_fg[code],
                weight=weight,
            )
            for code, weight in cleaned.items()
        ]
    )


def build_grouped_trait_display(
    weights: dict[str, float],
    functional_groups_by_code: dict[str, FunctionalGroup] | None = None,
) -> list[dict]:
    """Build sectioned trait display for templates."""
    if functional_groups_by_code is None:
        functional_groups_by_code = {fg.code: fg for fg in FunctionalGroup.objects.all()}

    sections: list[dict] = []
    for section in FUNCTIONAL_GROUP_UI_SECTIONS:
        if section['key'] == 'life_stage':
            traits = []
            for code in section['subtype_codes']:
                weight = weights.get(code)
                if not weight:
                    continue
                fg = functional_groups_by_code.get(code)
                traits.append({
                    'code': code,
                    'display_name': fg.display_name if fg else code,
                    'weight': weight,
                })
            if traits:
                sections.append({'title': section['title'], 'traits': traits})
            continue

        traits = []
        codes = []
        if section['parent_code']:
            codes.append(section['parent_code'])
        codes.extend(section['subtype_codes'])
        for code in codes:
            weight = weights.get(code)
            if not weight:
                continue
            fg = functional_groups_by_code.get(code)
            traits.append({
                'code': code,
                'display_name': fg.display_name if fg else code,
                'weight': weight,
            })
        if traits:
            sections.append({'title': section['title'], 'traits': traits})
    return sections
