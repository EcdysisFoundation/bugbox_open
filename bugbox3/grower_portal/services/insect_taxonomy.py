"""grower bug results taxonomy hierarchy from GBIF fields"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from bugbox3.grower_portal.constants import (
    GROWER_ACARI_MITE_GBIF_ORDERS,
    GROWER_ACARI_MITE_MORPHO_NAME,
    GROWER_ACARI_SUBCLASS_KEY,
    GROWER_TAXONOMY_UNSPECIFIED_CLASS,
    GROWER_TAXONOMY_UNSPECIFIED_ORDER,
)
from bugbox3.grower_portal.services.insect_display import display_family_for_grower
from bugbox3.samples.export_metrics import UNKNOWN_TAXON
from bugbox3.taxonomy.models import Morphospecies

GroupRank = Literal['order', 'subclass']


@dataclass(frozen=True)
class TaxonomyPlacement:
    class_key: str
    class_label: str
    group_key: str
    group_label: str
    group_rank: GroupRank
    family_label: str


def _is_acari_subclass(morpho: Morphospecies) -> bool:
    if morpho.name == GROWER_ACARI_MITE_MORPHO_NAME:
        return True
    return (
        morpho.gbif_class == 'Arachnida'
        and morpho.gbif_order in GROWER_ACARI_MITE_GBIF_ORDERS
    )


def resolve_grower_taxonomy(morpho: Morphospecies | None) -> TaxonomyPlacement | None:
    if not morpho:
        return None

    class_label = morpho.gbif_class.strip() if morpho.gbif_class else GROWER_TAXONOMY_UNSPECIFIED_CLASS
    class_key = class_label

    if _is_acari_subclass(morpho):
        group_key = GROWER_ACARI_SUBCLASS_KEY
        group_label = GROWER_ACARI_SUBCLASS_KEY
        group_rank: GroupRank = 'subclass'
        if morpho.name == GROWER_ACARI_MITE_MORPHO_NAME:
            family_label = display_family_for_grower(morpho)
        elif morpho.gbif_family:
            family_label = morpho.gbif_family
        else:
            family_label = display_family_for_grower(morpho)
    else:
        order = morpho.gbif_order.strip() if morpho.gbif_order else ''
        group_key = order or GROWER_TAXONOMY_UNSPECIFIED_ORDER
        group_label = group_key
        group_rank = 'order'
        if morpho.gbif_family:
            family_label = morpho.gbif_family
        else:
            family_label = display_family_for_grower(morpho)

    if family_label == UNKNOWN_TAXON:
        return None

    return TaxonomyPlacement(
        class_key=class_key,
        class_label=class_label,
        group_key=group_key,
        group_label=group_label,
        group_rank=group_rank,
        family_label=family_label,
    )


def accumulate_hierarchy_count(
    hierarchy: dict[str, dict[str, dict[str, float]]],
    placement: TaxonomyPlacement,
    count: float,
) -> None:
    class_bucket = hierarchy.setdefault(placement.class_key, {})
    group_bucket = class_bucket.setdefault(placement.group_key, {})
    group_bucket[placement.family_label] = group_bucket.get(placement.family_label, 0) + count


def build_families_hierarchy(
    hierarchy_counts: dict[str, dict[str, dict[str, float]]],
    *,
    group_ranks: dict[str, dict[str, GroupRank]],
) -> list[dict]:
    """build class - > group -> family tree for a site for the template"""
    classes_out: list[dict] = []

    for class_key in sorted(hierarchy_counts.keys(), key=str.lower):
        groups_data = hierarchy_counts[class_key]
        groups_out: list[dict] = []
        class_total = 0.0

        for group_key in sorted(groups_data.keys(), key=str.lower):
            families_map = groups_data[group_key]
            families = [
                {'family': family, 'total_count': round(count, 0)}
                for family, count in families_map.items()
            ]
            families.sort(key=lambda row: (-row['total_count'], row['family'].lower()))
            group_total = sum(families_map.values())
            class_total += group_total
            rank = group_ranks.get(class_key, {}).get(group_key, 'order')
            groups_out.append({
                'group_key': group_key,
                'group_label': group_key,
                'group_rank': rank,
                'total_count': round(group_total, 0),
                'families': families,
            })

        classes_out.append({
            'class_key': class_key,
            'class_label': class_key,
            'total_count': round(class_total, 0),
            'groups': groups_out,
        })

    return classes_out


def count_families_in_hierarchy(classes: list[dict]) -> int:
    total = 0
    for class_node in classes:
        for group in class_node.get('groups', []):
            total += len(group.get('families', []))
    return total
