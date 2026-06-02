"""Grower portal insect results from BugBox samples data"""

from __future__ import annotations

from collections import defaultdict
from datetime import date

from django.db.models import Prefetch

from bugbox3.grower_portal.constants import (
    INSECT_EXPORT_LEVEL,
    INSECT_GALLERY_MAX_PER_SITE,
    INSECT_GALLERY_MIN_CONFIDENCE,
    INSECT_MORPHO_EXPORT_LEVEL,
)
from bugbox3.grower_portal.models import GrowerSampleCodeMapping
from bugbox3.grower_portal.services.insect_display import display_family_for_grower
from bugbox3.grower_portal.services.insect_taxonomy import (
    accumulate_hierarchy_count,
    build_families_hierarchy,
    count_families_in_hierarchy,
    resolve_grower_taxonomy,
)
from bugbox3.libs.utilities import get_media_url
from bugbox3.samples import constants as samples_constants
from bugbox3.samples.export_metrics import (
    UNKNOWN_TAXON,
    compute_sample_morpho_counts,
    resolve_morphospecies_id,
    richness_taxon_names,
)
from bugbox3.samples.models import SiteVisit, Specimen, SpecimenImage


def get_grower_site_codes(grower) -> set[str]:
    return set(
        GrowerSampleCodeMapping.objects.filter(grower=grower)
        .values_list('sample_code__code', flat=True)
    )


def get_insect_available_years(grower) -> list[int]:
    codes = get_grower_site_codes(grower)
    if not codes:
        return []

    visit_years = set(
        SiteVisit.objects.filter(site__site_name__in=codes)
        .values_list('visit_date__year', flat=True)
        .distinct()
    ) - {None}

    codes_with_any_visit = set(
        SiteVisit.objects.filter(site__site_name__in=codes)
        .values_list('site__site_name', flat=True)
        .distinct()
    )

    fallback_years = set(
        GrowerSampleCodeMapping.objects.filter(grower=grower)
        .exclude(sample_code__code__in=codes_with_any_visit)
        .values_list('year_sampled', flat=True)
        .distinct()
    ) - {None}

    return sorted(visit_years | fallback_years, reverse=True)


def _specimens_prefetch():
    return Prefetch(
        'specimen_set',
        queryset=Specimen.objects.select_related('classification', 'ai_classification').prefetch_related(
            Prefetch(
                'specimenimage_set',
                queryset=SpecimenImage.objects.exclude(image_thumbnail_medium=''),
            ),
        ),
    )


def get_site_visits_for_grower_year(grower, year_int):
    codes = get_grower_site_codes(grower)
    if not codes:
        return SiteVisit.objects.none()

    return (
        SiteVisit.objects.filter(
            site__site_name__in=codes,
            visit_date__year=year_int,
        )
        .select_related('site', 'site__experiment')
        .prefetch_related(
            Prefetch('sample_set', queryset=_samples_with_specimens_queryset()),
        )
        .order_by('site__site_name', '-visit_date')
    )


def _samples_with_specimens_queryset():
    from bugbox3.samples.models import Sample

    return Sample.objects.prefetch_related(_specimens_prefetch())


def _fallback_site_codes(grower, year_int, codes_with_any_visit: set[str]) -> list[str]:
    return list(
        GrowerSampleCodeMapping.objects.filter(
            grower=grower,
            year_sampled=year_int,
        )
        .exclude(sample_code__code__in=codes_with_any_visit)
        .values_list('sample_code__code', flat=True)
        .distinct()
        .order_by('sample_code__code')
    )


def _format_visit_dates_hint(visit_dates: list[date]) -> str:
    if not visit_dates:
        return ''
    unique_dates = sorted(set(visit_dates))
    if len(unique_dates) == 1:
        return unique_dates[0].strftime('%b %d, %Y')
    first = unique_dates[0].strftime('%b %d')
    last = unique_dates[-1].strftime('%b %d, %Y')
    if len(unique_dates) == 2:
        return f'{first}–{last} (2 visits)'
    return f'{first}–{last} ({len(unique_dates)} visits)'


def _morpho_from_specimen(specimen):
    morphospecies_id = resolve_morphospecies_id(specimen, export_type=samples_constants.EXP_CSV_TYPE_ALL)
    morpho = specimen.classification if specimen.classification_id else specimen.ai_classification
    if morphospecies_id and morpho is None:
        morpho = specimen.classification or specimen.ai_classification
    return morpho


def _family_from_specimen(specimen) -> str:
    return display_family_for_grower(_morpho_from_specimen(specimen))


def _gallery_specimen_eligible(specimen) -> bool:
    """
    uses AI confidence as a proxy for whether the photo is clear enough to show to the grower
    """
    if specimen.confidence is None:
        return False
    return float(specimen.confidence) >= INSECT_GALLERY_MIN_CONFIDENCE


def _merge_specimen_hierarchy_into_site(site_data: dict, specimen):
    morpho = _morpho_from_specimen(specimen)
    placement = resolve_grower_taxonomy(morpho)
    if placement is None:
        return
    count = 1 + specimen.partial_count
    accumulate_hierarchy_count(site_data['hierarchy_counts'], placement, count)
    ranks = site_data['group_ranks'].setdefault(placement.class_key, {})
    ranks[placement.group_key] = placement.group_rank


def _merge_sample_metrics_into_site(
    site_data: dict,
    family_metrics: dict,
    morpho_metrics: dict,
    sample,
):
    """Family table from family-level counts; richness from morphospecies"""
    site_data['abundance_total'] += family_metrics['abundance']
    for family, count in family_metrics['taxon_counts'].items():
        if family == UNKNOWN_TAXON:
            continue
        site_data['family_counts'][family] = site_data['family_counts'].get(family, 0) + count
    site_data['morphos_present'].update(richness_taxon_names(morpho_metrics))
    for specimen in sample.specimen_set.all():
        _merge_specimen_hierarchy_into_site(site_data, specimen)


def select_gallery_images(
    pools: dict[str, list[dict]],
    family_order: list[str],
    *,
    max_total: int = INSECT_GALLERY_MAX_PER_SITE,
) -> list[dict]:
    """
    Round-robin across families until max_total or pools are filled
    """
    families = [f for f in family_order if pools.get(f)]
    if not families:
        return []

    selected: list[dict] = []
    picked_counts = {family: 0 for family in families}

    while len(selected) < max_total:
        added_this_round = False
        for family in families:
            if len(selected) >= max_total:
                break
            pool = pools[family]
            idx = picked_counts[family]
            if idx < len(pool):
                selected.append(pool[idx])
                picked_counts[family] += 1
                added_this_round = True
        if not added_this_round:
            break

    return selected


def build_gallery_images(
    visits,
    site_family_totals: dict[str, dict[str, float]],
) -> list[dict]:
    """round-robin across families"""
    pools_by_site: dict[str, dict[str, list[dict]]] = defaultdict(lambda: defaultdict(list))

    for visit in visits:
        site_code = visit.site.site_name
        visit_date = visit.visit_date
        for sample in visit.sample_set.all():
            for specimen in sample.specimen_set.all():
                if not _gallery_specimen_eligible(specimen):
                    continue
                family = _family_from_specimen(specimen)
                for image in specimen.specimenimage_set.all():
                    if not image.image_thumbnail_medium:
                        continue
                    pools_by_site[site_code][family].append({
                        'url': get_media_url(image.image_thumbnail_medium, image.public_image),
                        'family': family,
                        'site_code': site_code,
                        'visit_date': visit_date,
                        'primary_image': image.primary_image,
                        '_human_reviewed': bool(specimen.classification_id),
                        '_sort_date': visit_date,
                    })

    selected: list[dict] = []
    for site_code in sorted(pools_by_site.keys()):
        pools = pools_by_site[site_code]
        for family in pools:
            pools[family].sort(
                key=lambda item: (
                    item['_human_reviewed'],
                    item['_sort_date'],
                    item['primary_image'],
                ),
                reverse=True,
            )
            for item in pools[family]:
                item.pop('_sort_date', None)
                item.pop('_human_reviewed', None)
                item.pop('primary_image', None)

        family_totals = site_family_totals.get(site_code, {})
        family_order = sorted(
            pools.keys(),
            key=lambda f: (-family_totals.get(f, 0), f.lower()),
        )
        selected.extend(select_gallery_images(pools, family_order))

    return selected


def group_gallery_images_by_site(gallery_images: list[dict]) -> list[dict]:
    buckets: dict[str, list[dict]] = {}
    site_order: list[str] = []
    for img in gallery_images:
        code = img['site_code']
        if code not in buckets:
            buckets[code] = []
            site_order.append(code)
        buckets[code].append(img)
    return [{'site_code': code, 'images': buckets[code]} for code in site_order]


def build_insect_results_context(grower, year_int: int) -> dict:
    codes = get_grower_site_codes(grower)
    visits = list(get_site_visits_for_grower_year(grower, year_int))

    codes_with_any_visit = set(
        SiteVisit.objects.filter(site__site_name__in=codes)
        .values_list('site__site_name', flat=True)
        .distinct()
    ) if codes else set()

    site_groups: dict[str, dict] = defaultdict(lambda: {
        'abundance_total': 0,
        'family_counts': {},
        'hierarchy_counts': {},
        'group_ranks': {},
        'morphos_present': set(),
        'visit_dates': [],
    })

    for visit in visits:
        site_code = visit.site.site_name
        site_groups[site_code]['visit_dates'].append(visit.visit_date)
        for sample in visit.sample_set.all():
            family_metrics = compute_sample_morpho_counts(
                sample,
                level=INSECT_EXPORT_LEVEL,
                include_immatures_skipped=False,
                family_name_fn=display_family_for_grower,
            )
            if family_metrics is None:
                continue
            morpho_metrics = compute_sample_morpho_counts(
                sample,
                level=INSECT_MORPHO_EXPORT_LEVEL,
                include_immatures_skipped=False,
            )
            if morpho_metrics is None:
                continue
            _merge_sample_metrics_into_site(
                site_groups[site_code], family_metrics, morpho_metrics, sample,
            )

    summary_by_site = []
    families_by_site = []
    combined_morphos: set[str] = set()
    combined_abundance = 0

    for site_code in sorted(site_groups.keys()):
        data = site_groups[site_code]
        abundance = data['abundance_total']
        species_richness = len(data['morphos_present'])
        combined_abundance += abundance
        combined_morphos.update(data['morphos_present'])

        summary_by_site.append({
            'site_code': site_code,
            'abundance_total': round(abundance, 0) if abundance else None,
            'species_richness': species_richness if species_richness else None,
            'visit_dates_hint': _format_visit_dates_hint(data['visit_dates']),
            'has_bugbox_data': True,
        })

        for family, count in data['family_counts'].items():
            families_by_site.append({
                'family': family,
                'site_code': site_code,
                'total_count': round(count, 0),
            })

    for site_code in _fallback_site_codes(grower, year_int, codes_with_any_visit):
        summary_by_site.append({
            'site_code': site_code,
            'abundance_total': None,
            'species_richness': None,
            'visit_dates_hint': '',
            'has_bugbox_data': False,
        })

    summary_by_site.sort(key=lambda row: row['site_code'])

    families_by_site.sort(
        key=lambda row: (-row['total_count'], row['family'].lower(), row['site_code']),
    )

    families_grouped_by_site = []
    for site_code in sorted(site_groups.keys()):
        data = site_groups[site_code]
        classes = build_families_hierarchy(
            data['hierarchy_counts'],
            group_ranks=data['group_ranks'],
        )
        if not classes:
            continue
        families_grouped_by_site.append({
            'site_code': site_code,
            'classes': classes,
            'family_count': count_families_in_hierarchy(classes),
        })

    site_family_totals: dict[str, dict[str, float]] = {
        site_code: dict(data['family_counts'])
        for site_code, data in site_groups.items()
    }

    sites_with_data = sum(1 for row in summary_by_site if row['has_bugbox_data'])

    gallery_images = build_gallery_images(visits, site_family_totals)

    return {
        'summary_combined': {
            'site_count': sites_with_data,
            'abundance_total': round(combined_abundance, 0) if combined_abundance else None,
            'species_richness': len(combined_morphos) if combined_morphos else None,
        },
        'summary_by_site': summary_by_site,
        'families_by_site': families_by_site,
        'families_grouped_by_site': families_grouped_by_site,
        'gallery_images': gallery_images,
        'gallery_grouped_by_site': group_gallery_images_by_site(gallery_images),
    }


def grower_has_insect_data(grower, year_int: int) -> bool:
    if get_site_visits_for_grower_year(grower, year_int).exists():
        return True
    codes_with_any_visit = set(
        SiteVisit.objects.filter(site__site_name__in=get_grower_site_codes(grower))
        .values_list('site__site_name', flat=True)
        .distinct()
    )
    return bool(_fallback_site_codes(grower, year_int, codes_with_any_visit))
