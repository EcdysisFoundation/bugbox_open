"""Common-name lookup and display formatting for grower Bugs results."""

from __future__ import annotations

from bugbox3.grower_portal.constants import (
    GROWER_ACARI_SUBCLASS_KEY,
    GROWER_FAMILY_COMMON_NAME_ALIASES,
    GROWER_TAXONOMY_UNSPECIFIED_CLASS,
    GROWER_TAXONOMY_UNSPECIFIED_ORDER,
    INSECT_COMMON_NAMES,
)


def has_insect_common_name_entry(rank: str, taxon: str) -> bool:
    return (rank.lower(), taxon) in INSECT_COMMON_NAMES


def get_common_name(rank: str, taxon: str) -> str | None:
    common = INSECT_COMMON_NAMES.get((rank.lower(), taxon), '')
    return common or None


def format_taxon_display(
    scientific_label: str,
    rank: str,
    *,
    taxon_for_lookup: str | None = None,
    scientific_paren: str | None = None,
) -> str:
    """
    Return "Common (Scientific)" when a common name exists, else scientific_label alone.
    """
    if scientific_label in (GROWER_TAXONOMY_UNSPECIFIED_CLASS, GROWER_TAXONOMY_UNSPECIFIED_ORDER):
        return scientific_label

    alias = GROWER_FAMILY_COMMON_NAME_ALIASES.get(scientific_label)
    if alias is not None:
        lookup_rank, lookup_taxon, paren_taxon = alias
        common = get_common_name(lookup_rank, lookup_taxon)
        paren_label = scientific_paren or paren_taxon or scientific_label
        if common:
            return f'{common} ({paren_label})'
        return scientific_label

    lookup_taxon = taxon_for_lookup or scientific_label
    common = get_common_name(rank, lookup_taxon)
    paren_label = scientific_paren or scientific_label
    if common:
        return f'{common} ({paren_label})'
    return scientific_label


def format_class_display(class_label: str) -> str:
    return format_taxon_display(class_label, 'class')


def format_group_display(group_label: str, group_rank: str) -> str:
    if group_label == GROWER_TAXONOMY_UNSPECIFIED_ORDER:
        return group_label
    if group_rank == 'subclass' and group_label == GROWER_ACARI_SUBCLASS_KEY:
        common = get_common_name('class', 'Arachnida')
        if common:
            return f'{common} ({group_label})'
        return group_label
    return format_taxon_display(group_label, group_rank)


def format_family_display(family_label: str) -> str:
    return format_taxon_display(family_label, 'family')


def enrich_hierarchy_display_labels(classes: list[dict]) -> list[dict]:
    """Add display_label to class, group, and family nodes in a hierarchy tree."""
    for class_node in classes:
        class_label = class_node['class_label']
        if class_label != GROWER_TAXONOMY_UNSPECIFIED_CLASS:
            class_node['display_label'] = format_class_display(class_label)
        for group_node in class_node.get('groups', []):
            group_node['display_label'] = format_group_display(
                group_node['group_label'],
                group_node.get('group_rank', 'order'),
            )
            for family_row in group_node.get('families', []):
                family_row['display_label'] = format_family_display(family_row['family'])
    return classes
