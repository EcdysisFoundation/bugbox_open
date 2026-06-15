"""Shared specimen counting logic for experiment CSV export and grower insect results"""

from __future__ import annotations

from bugbox3.taxonomy.models import Morphospecies
from bugbox3.taxonomy.utils import get_immature_morphospecies_ids, get_skip_morphospecies_ids

from . import constants
from .calculations import get_indices

UNKNOWN_TAXON = 'Not identified'
UNSPECIFIED_FAMILY = 'Unspecified Family'


def normalize_export_level(level: str) -> str:
    return 'family' if level == 'family' else 'morphospecies'


def resolve_morphospecies_id(specimen, export_type: str):
    if export_type == constants.EXP_CSV_TYPE_AI:
        return specimen.ai_classification_id
    if export_type == constants.EXP_CSV_TYPE_REVIEWED:
        if (
            specimen.acceptance == constants.ACCEPTANCE_PENDING
            and specimen.ai_classification_id
        ):
            return None
        return specimen.classification_id
    return specimen.classification_id or specimen.ai_classification_id


def taxon_name_from_morpho(
    morpho: Morphospecies | None,
    level: str,
    unknown: str = UNKNOWN_TAXON,
    *,
    family_name_fn=None,
) -> str:
    if not morpho:
        return unknown
    if level == 'family':
        if morpho.gbif_family:
            return morpho.gbif_family
        if family_name_fn is not None:
            return family_name_fn(morpho)
        return UNSPECIFIED_FAMILY
    return morpho.name


def taxon_header_fields(morpho: Morphospecies | None, level: str, name: str) -> dict:
    if not morpho:
        return {'order': '', 'family': '', 'species': ''}
    if level == 'family':
        return {'order': morpho.gbif_order or '', 'family': morpho.gbif_family or '', 'species': ''}
    return {
        'order': morpho.gbif_order or '',
        'family': morpho.gbif_family or '',
        'species': morpho.gbif_species or morpho.gbif_genus or '',
    }


def filter_specimens_for_export(specimens, export_type: str, include_immatures_skipped: bool):
    if include_immatures_skipped or export_type == constants.EXP_CSV_TYPE_AI:
        return specimens
    skip_ids = get_skip_morphospecies_ids()
    immature_ids = get_immature_morphospecies_ids()
    return specimens.exclude(classification_id__in=skip_ids + immature_ids)


def compute_sample_morpho_counts(
    sample,
    *,
    export_type=constants.EXP_CSV_TYPE_ALL,
    level='morphospecies',
    include_immatures_skipped=False,
    specimens=None,
    compute_indices=True,
    indices_keys=None,
    family_name_fn=None,
):
    level = normalize_export_level(level)
    unknown = UNKNOWN_TAXON
    if export_type == constants.EXP_CSV_TYPE_REVIEWED:
        unknown = f'{unknown} or reviewed'

    skip_morphospecies_ids = get_skip_morphospecies_ids()
    immature_morphospecies_ids = get_immature_morphospecies_ids()
    if include_immatures_skipped:
        skip_morphospecies_ids = []
        immature_morphospecies_ids = []

    if specimens is None:
        specimens = sample.specimen_set.all()
    specimens = filter_specimens_for_export(specimens, export_type, include_immatures_skipped)

    if not specimens.exists() and not sample.completed:
        return None

    taxon_counts: dict[str, float] = {unknown: 0}
    taxon_headers: dict[str, dict] = {unknown: {'order': '', 'family': '', 'species': ''}}
    excluded_names_in_row: set[str] = set()
    abundance = 0

    morpho_cache: dict[int, Morphospecies] = {}

    for specimen in specimens:
        morphospecies_id = resolve_morphospecies_id(specimen, export_type)
        morpho = None
        if morphospecies_id:
            morpho = morpho_cache.get(morphospecies_id)
            if morpho is None:
                morpho = Morphospecies.objects.get(id=morphospecies_id)
                morpho_cache[morphospecies_id] = morpho

        name = taxon_name_from_morpho(
            morpho, level, unknown=unknown, family_name_fn=family_name_fn,
        )
        taxon_headers[name] = taxon_header_fields(morpho, level, name)

        total = 1 + (specimen.partial_count or 0)
        taxon_counts[name] = taxon_counts.get(name, 0) + total
        abundance += total

        if morphospecies_id in immature_morphospecies_ids or morphospecies_id in skip_morphospecies_ids:
            excluded_names_in_row.add(name)
        if morpho and morpho.exclude_from_export:
            excluded_names_in_row.add(name)

    non_species_keys = set(constants.EXP_HEADERS_ARR)
    if indices_keys:
        non_species_keys.update(indices_keys)

    excluded_for_indices = excluded_names_in_row.union({unknown})
    row_for_indices = {
        k: v for k, v in taxon_counts.items()
        if k not in excluded_for_indices and k not in non_species_keys
    }
    n_for_indices = sum(row_for_indices.values())
    indices = get_indices(n_for_indices, row_for_indices, list(non_species_keys))

    result = {
        'abundance': abundance,
        'species_richness': indices['species_richness'],
        'taxon_counts': taxon_counts,
        'taxon_headers': taxon_headers,
        'excluded_names': excluded_names_in_row,
    }
    if compute_indices:
        result['indices'] = indices
    return result


def richness_taxon_names(metrics: dict, unknown: str = UNKNOWN_TAXON) -> set[str]:
    """Taxon names that contribute to species_richness for one sample (export rules)."""
    excluded = metrics.get('excluded_names', set()) | {unknown}
    return {
        name for name, count in metrics['taxon_counts'].items()
        if count and name not in excluded
    }


def compute_indices_from_pooled_taxon_counts(
    taxon_counts: dict[str, float],
    excluded_names: set[str],
    *,
    unknown: str = UNKNOWN_TAXON,
) -> dict:
    """Hill numbers and related indices from pooled morphospecies counts"""
    non_species_keys = set(constants.EXP_HEADERS_ARR)
    excluded_for_indices = excluded_names.union({unknown})
    row_for_indices = {
        k: v for k, v in taxon_counts.items()
        if k not in excluded_for_indices and k not in non_species_keys
    }
    n = sum(row_for_indices.values())
    return get_indices(n, row_for_indices, list(non_species_keys))


def common_species_h2_display(indices: dict) -> float | None:
    """Rounded Hill H2 for grower-facing display, or None when not applicable (insect results)"""
    h2 = indices.get('hill_H2')
    if h2 in ('N/A', None) or not indices.get('abundance'):
        return None
    return round(h2, 1)
