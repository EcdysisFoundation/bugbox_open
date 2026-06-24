"""Aggregation of functional groups for grower insect results."""

from __future__ import annotations

from bugbox3.grower_portal.constants import GROWER_FUNCTIONAL_GROUP_CATEGORIES

FUNCTIONAL_GROUP_KEYS = tuple(cat['key'] for cat in GROWER_FUNCTIONAL_GROUP_CATEGORIES)


def accumulate_specimen_functional_groups(
    *,
    morphospecies_id: int | None,
    count: float,
    category_totals: dict[str, float],
    unclassified_count: float,
    grower_weights_by_morpho_id: dict[int, dict[str, float]],
) -> float:
    """Add one specimen's weighted contribution; returns updated unclassified_count."""
    if morphospecies_id is None:
        return unclassified_count + count
    weights = grower_weights_by_morpho_id.get(int(morphospecies_id))
    if weights is None:
        return unclassified_count + count
    for key, weight in weights.items():
        category_totals[key] = category_totals.get(key, 0.0) + count * weight
    return unclassified_count


def build_functional_group_summary(
    category_totals: dict[str, float],
    *,
    unclassified_count: float,
    abundance_total: float,
) -> dict:
    mapped_total = sum(category_totals.get(key, 0.0) for key in FUNCTIONAL_GROUP_KEYS)
    categories: list[dict] = []
    for meta in GROWER_FUNCTIONAL_GROUP_CATEGORIES:
        key = meta['key']
        count = category_totals.get(key, 0.0)
        percent = (100.0 * count / mapped_total) if mapped_total else None
        categories.append({
            'key': key,
            'label': meta['label'],
            'color': meta['color'],
            'count': round(count, 1),
            'percent': round(percent, 1) if percent is not None else None,
        })

    unclassified_percent = (
        (100.0 * unclassified_count / abundance_total) if abundance_total else None
    )
    return {
        'categories': categories,
        'mapped_total': round(mapped_total, 1),
        'unclassified_count': round(unclassified_count, 1),
        'abundance_total': round(abundance_total, 1),
        'unclassified_percent': (
            round(unclassified_percent, 1) if unclassified_percent is not None else None
        ),
    }


FUNCTIONAL_GROUP_CHART_ELEMENT_ID = 'fg-chart-ecological-roles'


def _summary_to_chart_row(summary: dict, label: str) -> dict:
    return {
        'label': label,
        'categories': summary['categories'],
    }


def build_functional_group_chart_payload(insect_ctx: dict) -> dict | None:
    """Build ApexCharts payload: Combined row when 2+ sites, else site row only."""
    combined = insect_ctx.get('functional_groups_combined')
    by_site = insect_ctx.get('functional_groups_by_site') or []

    site_rows: list[dict] = []
    for site_fg in by_site:
        if site_fg.get('mapped_total'):
            site_rows.append(_summary_to_chart_row(site_fg, f"Site {site_fg['site_code']}"))

    rows: list[dict] = []
    if len(site_rows) > 1 and combined and combined.get('mapped_total'):
        rows.append(_summary_to_chart_row(combined, 'Combined (all sites)'))
    rows.extend(site_rows)

    if not rows:
        return None

    return {
        'element_id': FUNCTIONAL_GROUP_CHART_ELEMENT_ID,
        'rows': rows,
        'series_meta': [
            {'key': meta['key'], 'name': meta['label'], 'color': meta['color']}
            for meta in GROWER_FUNCTIONAL_GROUP_CATEGORIES
        ],
        'combined_unclassified_count': combined.get('unclassified_count') if combined else 0,
        'combined_unclassified_percent': (
            combined.get('unclassified_percent') if combined else None
        ),
    }


def empty_category_totals() -> dict[str, float]:
    return {key: 0.0 for key in FUNCTIONAL_GROUP_KEYS}
