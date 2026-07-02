"""Load and save morphospecies functional-group traits (active/inactive)."""

from __future__ import annotations

from django.core.exceptions import ValidationError

from bugbox3.taxonomy.functional_group_config import ALL_TRAIT_CODES, FUNCTIONAL_GROUP_UI_SECTIONS
from bugbox3.taxonomy.functional_group_validation import (
    infer_missing_parent_traits,
    validate_functional_group_traits,
)
from bugbox3.taxonomy.models import FunctionalGroup, Morphospecies, MorphospeciesFunctionalGroup


def get_active_traits_for_morphospecies(morphospecies: Morphospecies) -> dict[str, bool]:
    rows = (
        MorphospeciesFunctionalGroup.objects.filter(morphospecies=morphospecies, active=True)
        .select_related('functional_group')
    )
    return {row.functional_group.code: True for row in rows}


def get_active_traits_for_morphospecies_ids(
    morphospecies_ids: set[int] | list[int],
) -> dict[int, dict[str, bool]]:
    if not morphospecies_ids:
        return {}
    result: dict[int, dict[str, bool]] = {}
    rows = (
        MorphospeciesFunctionalGroup.objects.filter(
            morphospecies_id__in=morphospecies_ids,
            active=True,
        )
        .select_related('functional_group')
    )
    for row in rows:
        result.setdefault(row.morphospecies_id, {})[row.functional_group.code] = True
    return result


def set_active_traits_for_morphospecies(
    morphospecies: Morphospecies,
    traits: dict[str, bool],
    *,
    validate: bool = True,
) -> None:
    cleaned = {
        code: True
        for code, active in traits.items()
        if active and code in ALL_TRAIT_CODES
    }
    cleaned = infer_missing_parent_traits(cleaned)
    if validate:
        validate_functional_group_traits(cleaned)

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
                active=True,
            )
            for code in cleaned
        ]
    )


def build_grouped_trait_display(
    traits: dict[str, bool],
    functional_groups_by_code: dict[str, FunctionalGroup] | None = None,
) -> list[dict]:
    """Build sectioned trait display for templates."""
    if functional_groups_by_code is None:
        functional_groups_by_code = {fg.code: fg for fg in FunctionalGroup.objects.all()}

    sections: list[dict] = []
    for section in FUNCTIONAL_GROUP_UI_SECTIONS:
        if section['key'] == 'life_stage':
            section_traits = []
            for code in section['subtype_codes']:
                if not traits.get(code):
                    continue
                fg = functional_groups_by_code.get(code)
                section_traits.append({
                    'code': code,
                    'display_name': fg.display_name if fg else code,
                })
            if section_traits:
                sections.append({'title': section['title'], 'traits': section_traits})
            continue

        section_traits = []
        codes = []
        if section['parent_code']:
            codes.append(section['parent_code'])
        codes.extend(section['subtype_codes'])
        for code in codes:
            if not traits.get(code):
                continue
            fg = functional_groups_by_code.get(code)
            section_traits.append({
                'code': code,
                'display_name': fg.display_name if fg else code,
            })
        if section_traits:
            sections.append({'title': section['title'], 'traits': section_traits})
    return sections
