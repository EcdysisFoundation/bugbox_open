import json
from collections import Counter, defaultdict
from datetime import date

from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse

from bugbox3.core.permissions import IS_GROWER_USER
from bugbox3.libs.utilities import get_json_context

from ...constants import (
    CATEGORY_CHOICES,
    CATEGORY_DISPLAY_META,
    CATEGORY_RESULT_TYPE_MAP,
    LABEL_PROJECT_CHOICES,
    RESULT_TYPE_CHOICES,
    RESULT_TYPE_FACTOR_MAPPING,
)
from ...forms.grower.forms import ResultsFilterForm
from ...middleware import get_user_timezone
from ...models import CSVImportFieldValue, CSVImportLog, CSVImportRow
from ...services.bird_references import build_all_about_birds_overview_url
from ...services.insect_results import (
    build_insect_results_context,
    get_insect_available_years,
    grower_has_insect_data,
)

_RESULT_TYPE_DISPLAY = dict(RESULT_TYPE_CHOICES)
_CATEGORY_DISPLAY = dict(CATEGORY_CHOICES)


def _uses_sample_code_grower_join(project_type: str, result_type: str) -> bool:
    """
    Ignite soil uploads scope rows by SiteTransect
    bird uploads attach to SampleCode for both projects (ignite & Avalanche)
    """
    return result_type == 'birds' or project_type != 'ignite'


def _field_value_filters(grower, year_int, project_type, result_type, category=None):
    """Build ORM filter kwargs scoping CSVImportFieldValue to a grower."""
    if _uses_sample_code_grower_join(project_type, result_type):
        prefix = 'row__sample_code__grower_mappings'
    else:
        prefix = 'row__site_transect__site_code__grower_mappings'
    filters = {
        f'{prefix}__grower': grower,
        f'{prefix}__year_sampled': year_int,
        'row__import_log__project_type': project_type,
        'row__import_log__result_type': result_type,
    }
    if category:
        filters['row__import_log__category'] = category
    return filters


def _field_value_qs(grower, year_int, project_type, result_type, depth=None, category=None):
    """Return a CSVImportFieldValue queryset with appropriate select_related."""
    filters = _field_value_filters(grower, year_int, project_type, result_type, category=category)
    if depth:
        filters['row__depth'] = depth
    related = ['row', 'row__import_log']
    if _uses_sample_code_grower_join(project_type, result_type):
        related.append('row__sample_code')
    else:
        related.extend(['row__site_transect', 'row__site_transect__site_code'])
    return (
        CSVImportFieldValue.objects
        .filter(**filters)
        .select_related(*related)
        .distinct()
        .order_by('row', 'field_name', 'field_value')
    )


def _get_depth_options(grower, year, project_type, result_type='basic'):
    if not year:
        return []
    try:
        year_int = int(year)
    except (ValueError, TypeError):
        return []

    if project_type == 'ignite':
        grower_filter = {
            'site_transect__site_code__grower_mappings__grower': grower,
            'site_transect__site_code__grower_mappings__year_sampled': year_int,
        }
    else:
        grower_filter = {
            'sample_code__grower_mappings__grower': grower,
            'sample_code__grower_mappings__year_sampled': year_int,
        }

    depth_values = (
        CSVImportRow.objects
        .filter(
            **grower_filter,
            import_log__project_type=project_type,
            import_log__result_type=result_type,
        )
        .filter(depth__isnull=False)
        .exclude(depth='')
        .values_list('depth', flat=True)
        .distinct()
    )

    parsed = {}
    for depth_str in depth_values:
        if depth_str not in parsed and '-' in depth_str:
            parts = depth_str.split('-', 1)
            try:
                parsed[depth_str] = (int(parts[0].strip()), int(parts[1].strip()))
            except ValueError:
                pass

    return [(d, d) for d, _ in sorted(parsed.items(), key=lambda x: x[1])]


def _is_numeric(value):
    if value is None or value == '':
        return False
    s = str(value).strip()
    try:
        float(s)
        return True
    except (ValueError, TypeError):
        pass
    return _is_numeric_range(s)


def _is_numeric_range(s: str) -> bool:
    """True for strings like '88-91' or '10.5-12.0'."""
    parts = s.split('-')
    if len(parts) != 2:
        return False
    try:
        float(parts[0].strip())
        float(parts[1].strip())
        return True
    except (ValueError, TypeError):
        return False


def _to_float(value) -> float | None:
    """
    Convert a value to float for averaging
    Range strings ('88-91') uses midpoint
    """
    if value is None or value == '':
        return None
    s = str(value).strip()
    try:
        return float(s)
    except (ValueError, TypeError):
        pass
    parts = s.split('-')
    if len(parts) == 2:
        try:
            return (float(parts[0].strip()) + float(parts[1].strip())) / 2
        except (ValueError, TypeError):
            pass
    return None


def _aggregate_field_values(field_values):
    if not field_values:
        return {}
    groups = defaultdict(list)
    for fv in field_values:
        groups[fv.field_name].append(fv.field_value)

    aggregated = {}
    for field_name, values in groups.items():
        non_empty = [v for v in values if v is not None and str(v).strip()]
        if not non_empty:
            aggregated[field_name] = None
            continue
        numeric_floats = [_to_float(v) for v in non_empty if _is_numeric(v)]
        numeric_floats = [f for f in numeric_floats if f is not None]
        if numeric_floats:
            aggregated[field_name] = sum(numeric_floats) / len(numeric_floats)
        else:
            non_numeric = [str(v).strip() for v in non_empty]
            aggregated[field_name] = Counter(non_numeric).most_common(1)[0][0]

    return aggregated


def _organize_results_by_mapping(field_values, result_type):
    factor_mapping = RESULT_TYPE_FACTOR_MAPPING.get(result_type)
    if not factor_mapping:
        return {}

    aggregated_values = _aggregate_field_values(field_values)
    if not aggregated_values:
        return {}

    individual_by_field = {}
    for fv in field_values:
        row = fv.row
        if not row:
            continue
        if row.site_transect_id:
            label = f'{row.site_transect.site_code.code} ({row.site_transect.transect_number})'
        elif row.sample_code_id:
            label = row.sample_code.code
        else:
            label = None
        if label:
            individual_by_field.setdefault(fv.field_name, []).append({
                'label': label,
                'value': fv.field_value,
                'is_numeric': _is_numeric(fv.field_value),
            })

    organized_results = {}
    for table_name, factors in factor_mapping.items():
        table_data = []
        for factor_display_name, factor_info in factors.items():
            field_name = factor_info.get('field_name')
            if field_name and field_name in aggregated_values:
                value = aggregated_values[field_name]
                table_data.append({
                    'factor_name': factor_display_name,
                    'field_name': field_name,
                    'units': factor_info.get('units'),
                    'value': value,
                    'has_value': value is not None,
                    'is_numeric': _is_numeric(value) if value is not None else False,
                    'summary': factor_info.get('summary', ''),
                    'description': factor_info.get('description', ''),
                    'individual_values': individual_by_field.get(field_name, []),
                })
        if table_data:
            organized_results[table_name] = table_data

    return organized_results


# Bird-specific helpers

def _get_bird_context(grower, year_int, project_type):
    """
    Return bird-specific display data:
      - summary: avg Abundance, avg Richness, survey count
      - survey_rows: individual survey events (date, richness, abundance, conditions)
      - family_map: {species_name: family_name}  (CSVImportLog.ingestion_metadata family_map)
      - species_by_family: {family: [{species, avg_count}]}
    """
    prefix = 'row__sample_code__grower_mappings'

    filters = {
        f'{prefix}__grower': grower,
        f'{prefix}__year_sampled': year_int,
        'row__import_log__project_type': project_type,
        'row__import_log__result_type': 'birds',
        'row__import_log__category': 'birds',
    }

    fvs = (
        CSVImportFieldValue.objects
        .filter(**filters)
        .select_related('row', 'row__import_log', 'row__sample_code')
        .order_by('row__row_number', 'field_name')
    )

    # Aggregate factor fields
    organized = _organize_results_by_mapping(list(fvs), 'birds')

    # Build per-survey rows for history table
    surveys_by_row: dict = {}
    for fv in fvs:
        rid = fv.row_id
        if rid not in surveys_by_row:
            surveys_by_row[rid] = {}
        if "site_code" not in surveys_by_row[rid]:
            surveys_by_row[rid]["site_code"] = fv.row.sample_code.code if fv.row and fv.row.sample_code else ""
        surveys_by_row[rid][fv.field_name] = fv.field_value

    survey_rows = []
    for rid, row_data in surveys_by_row.items():
        survey_rows.append({
            'site_code': row_data.get('site_code', ''),
            'date': row_data.get('Date', ''),
            'time': row_data.get('Time', ''),
            'abundance': row_data.get('Abundance', ''),
            'richness': row_data.get('Richness', ''),
            'temp_f': row_data.get('Temp \ufffdF', '') or row_data.get('Temp °F', '') or row_data.get('Temp F', ''),
            'distance_mi': (
                row_data.get('Distance mi', '')
                or row_data.get('Distance MI', '')
                or row_data.get('Distance Mi', '')
            ),
            'duration_min': row_data.get('Duration (min)', ''),
        })
    # Per-site survey abundance and survey count
    abundance_total_by_site: dict[str, float] = defaultdict(float)
    abundance_survey_count_by_site: dict[str, int] = defaultdict(int)
    for s in survey_rows:
        site = str(s.get("site_code") or "").strip()
        if not site:
            continue
        abundance_val = s.get("abundance", "")
        if _is_numeric(abundance_val):
            f = _to_float(abundance_val)
            if f is not None:
                abundance_total_by_site[site] += f
                abundance_survey_count_by_site[site] += 1

    # Per-site survey conditions
    conditions_by_site_map: dict[str, dict] = {}
    for s in survey_rows:
        site = str(s.get("site_code") or "").strip()
        if not site:
            continue
        current_key = f"{s.get('date', '')} {s.get('time', '')}"
        prev = conditions_by_site_map.get(site)
        prev_key = f"{prev.get('date', '')} {prev.get('time', '')}" if prev else ""
        if not prev or current_key > prev_key:
            conditions_by_site_map[site] = s

    conditions_by_site = [
        {
            "site_code": site,
            "distance_mi": row.get("distance_mi", ""),
            "duration_min": row.get("duration_min", ""),
        }
        for site, row in sorted(conditions_by_site_map.items(), key=lambda x: x[0])
    ]

    # Retrieve family_map from the most recent import log for this grower/year/project
    family_map: dict = {}
    species_by_family: dict = defaultdict(list)

    log_qs = (
        CSVImportLog.objects
        .filter(
            **{
                'csvimportrow__sample_code__grower_mappings__grower': grower,
                'project_type': project_type,
                'result_type': 'birds',
                'category': 'birds',
            }
        )
        .order_by('-import_date')
        .distinct()
    )
    for log in log_qs:
        meta = log.ingestion_metadata or {}
        if meta.get('family_map'):
            family_map = meta['family_map']
            break
        try:
            desc = json.loads(log.description) if log.description else {}
            if isinstance(desc, dict) and 'family_map' in desc:
                family_map = desc['family_map']
                break
        except (json.JSONDecodeError, TypeError):
            pass

    # Build species counts per family per site (no cross-site averaging)
    species_richness_by_site: dict[str, int] = {}
    species_richness_combined: int = 0
    if family_map:
        non_species_keys = {
            'Date', 'Time', 'Duration (min)', 'Distance KM', 'Distance mi', 'Distance MI', 'Distance Mi',
            'Temp \ufffdC', 'Temp °C', 'Temp \ufffdF', 'Temp °F', 'Temp F',
            'Matrix Score', 'Site Code', 'Abundance', 'Richness', '',
            # Internal key added for the survey history table; not a species column.
            'site_code',
        }
        # key: (species_col_name, site_code) -> [counts...]
        species_totals: dict = defaultdict(list)
        present_species_by_site: dict[str, set] = defaultdict(set)
        present_species_combined: set = set()
        for row_data in surveys_by_row.values():
            site_code = row_data.get('site_code') or row_data.get('Site Code') or ''
            site_code = str(site_code).strip()
            for col, val in row_data.items():
                if col in non_species_keys:
                    continue
                if _is_numeric(val) and float(val) > 0:
                    species_totals[(col, site_code)].append(float(val))
                    present_species_by_site[site_code].add(col)
                    present_species_combined.add(col)

        for (species, site_code), counts in species_totals.items():
            family = family_map.get(species, 'Unknown Family')
            total = sum(counts) if counts else 0
            species_by_family[family].append({
                'species': species,
                'site_code': site_code,
                'total_count': round(total, 2),
                'visit_count': len(counts),
                'all_about_birds_url': build_all_about_birds_overview_url(species),
            })

        species_richness_by_site = {
            site: len(species_set)
            for site, species_set in present_species_by_site.items()
            if site
        }
        species_richness_combined = len(present_species_combined)

        # Sort families alphabetically and species within each family by total_count desc
        species_by_family = {
            fam: sorted(spp, key=lambda x: x['total_count'], reverse=True)
            for fam, spp in sorted(species_by_family.items())
        }

    per_site_summary = []
    for site in sorted(set(list(abundance_total_by_site.keys()) + list(species_richness_by_site.keys()))):
        per_site_summary.append({
            'site_code': site,
            'survey_count': abundance_survey_count_by_site.get(site, 0),
            'abundance_total': (
                round(abundance_total_by_site.get(site, 0.0), 0)
                if site in abundance_total_by_site
                else None
            ),
            'species_richness': species_richness_by_site.get(site, None),
        })

    return {
        'organized_results': organized,
        'survey_rows': sorted(survey_rows, key=lambda x: x.get('date', '') or '', reverse=True),
        'survey_count': len(survey_rows),
        'conditions_by_site': conditions_by_site,
        'family_map': family_map,
        'species_by_family': dict(species_by_family),
        'summary_combined': {
            'abundance_total': round(sum(abundance_total_by_site.values()), 0) if abundance_total_by_site else None,
            'species_richness': species_richness_combined if species_richness_combined else None,
        },
        'summary_by_site': per_site_summary,
    }


@login_required
@permission_required(IS_GROWER_USER, raise_exception=True)
def basic_results_ajax(request):
    grower = request.user
    year = request.GET.get('year', '')
    project_type = request.GET.get('project_type', 'avalanche')
    depth = request.GET.get('depth', '')

    organized_results = {}
    try:
        year_int = int(year)
        field_values = _field_value_qs(grower, year_int, project_type, 'basic', depth=depth)
        organized_results = _organize_results_by_mapping(field_values, 'basic')
    except (ValueError, TypeError):
        pass

    return render(request, 'grower_portal/grower/_basic_results_tables.html', {
        'organized_results': organized_results,
    })


@login_required
@permission_required(IS_GROWER_USER, raise_exception=True)
def depth_options_ajax(request):
    grower = request.user
    year = request.GET.get('year')
    project_type = request.GET.get('project_type')
    result_type = request.GET.get('result_type', 'basic')

    depth_options = []
    if year and project_type and result_type in ('basic', 'haney', 'plfa'):
        depth_options = _get_depth_options(grower, year, project_type, result_type)

    return JsonResponse({
        'options': [{'value': value, 'label': label} for value, label in depth_options],
    })


@login_required
@permission_required(IS_GROWER_USER, raise_exception=True)
def results(request):
    grower = request.user

    # determine available years (union across all result types)
    avalanche_year_set = set(
        CSVImportFieldValue.objects.filter(
            row__sample_code__grower_mappings__grower=grower,
            row__import_log__project_type='avalanche',
        ).order_by().values_list(
            'row__sample_code__grower_mappings__year_sampled', flat=True
        ).distinct()
    ) - {None}

    ignite_year_from_transect = set(
        CSVImportFieldValue.objects.filter(
            row__site_transect__site_code__grower_mappings__grower=grower,
            row__import_log__project_type='ignite',
        ).order_by().values_list(
            'row__site_transect__site_code__grower_mappings__year_sampled', flat=True
        ).distinct()
    ) - {None}
    ignite_year_from_sample_code = set(
        CSVImportFieldValue.objects.filter(
            row__sample_code__grower_mappings__grower=grower,
            row__import_log__project_type='ignite',
        ).order_by().values_list(
            'row__sample_code__grower_mappings__year_sampled', flat=True
        ).distinct()
    ) - {None}
    ignite_year_set = ignite_year_from_transect | ignite_year_from_sample_code

    insect_year_set = set(get_insect_available_years(grower))

    available_years = sorted(
        avalanche_year_set | ignite_year_set | insect_year_set,
        reverse=True,
    ) or [date.today().year]

    years_to_project_types = {}
    for y in avalanche_year_set:
        years_to_project_types.setdefault(str(y), []).append('avalanche')
    for y in ignite_year_set:
        years_to_project_types.setdefault(str(y), []).append('ignite')

    default_year = available_years[0]
    year_str = request.GET.get('year', '')
    depth = request.GET.get('depth', '')

    try:
        year = int(year_str) if year_str else default_year
    except (ValueError, TypeError):
        year = default_year

    available_for_year = years_to_project_types.get(str(year), [])
    default_project_type = available_for_year[0] if available_for_year else 'avalanche'
    project_type = request.GET.get('project_type', default_project_type)

    if request.GET:
        form = ResultsFilterForm(data=request.GET, available_years=available_years)
        if form.is_valid():
            year = form.cleaned_data.get('year') or year
            project_type = form.cleaned_data.get('project_type') or project_type
    else:
        form = ResultsFilterForm(
            initial={'year': year, 'project_type': project_type},
            available_years=available_years,
        )

    year_int = int(year)

    # build categories_data
    categories_data = []

    for cat_value, cat_label in CATEGORY_CHOICES:
        result_types_for_cat = CATEGORY_RESULT_TYPE_MAP.get(cat_value, [])
        sections = []

        for rt_value in result_types_for_cat:
            rt_display = _RESULT_TYPE_DISPLAY.get(rt_value, rt_value)

            if rt_value == 'birds':
                bird_ctx = _get_bird_context(grower, year_int, project_type)
                has_data = bool(bird_ctx['survey_count'])
                sections.append({
                    'result_type': rt_value,
                    'display': rt_display,
                    'is_birds': True,
                    'is_insects': False,
                    'has_data': has_data,
                    'bird_data': bird_ctx,
                    'depth_options': [],
                })
            elif rt_value == 'insects':
                insect_ctx = build_insect_results_context(grower, year_int)
                has_data = grower_has_insect_data(grower, year_int)
                sections.append({
                    'result_type': rt_value,
                    'display': rt_display,
                    'is_birds': False,
                    'is_insects': True,
                    'has_data': has_data,
                    'insect_data': insect_ctx,
                    'depth_options': [],
                })
            else:
                depth_options = _get_depth_options(grower, year, project_type, rt_value)
                fv_qs = _field_value_qs(
                    grower, year_int, project_type, rt_value,
                    depth=depth,
                    category=cat_value,
                )
                organized = _organize_results_by_mapping(fv_qs, rt_value)
                sections.append({
                    'result_type': rt_value,
                    'display': rt_display,
                    'is_birds': False,
                    'is_insects': False,
                    'has_data': bool(organized),
                    'organized_results': organized,
                    'depth_options': depth_options,
                })

        has_any = any(s['has_data'] for s in sections)
        categories_data.append({
            'value': cat_value,
            'label': cat_label,
            'icon': CATEGORY_DISPLAY_META.get(cat_value, {}).get('icon', 'fa-folder'),
            'sections': sections,
            'has_data': has_any,
        })

    depth_options_basic = _get_depth_options(grower, year, project_type, 'basic')

    insect_functional_group_chart = None
    for cat in categories_data:
        for section in cat.get('sections', []):
            if section.get('is_insects') and section.get('insect_data'):
                insect_functional_group_chart = section['insect_data'].get(
                    'functional_group_chart',
                )
                break
        if insect_functional_group_chart is not None:
            break

    return render(request, 'grower_portal/grower/results.html', {
        'form': form,
        'categories_data': categories_data,
        'depth_options': depth_options_basic,
        'year': year,
        'project_type': project_type,
        'project_type_display': dict(LABEL_PROJECT_CHOICES).get(project_type, project_type),
        'depth': depth,
        'user_timezone': get_user_timezone(request),
        'json_context': get_json_context({
            'factor_detail_url': reverse('grower_portal:factor_detail'),
            'basic_results_url': reverse('grower_portal:basic_results_ajax'),
            'year': year,
            'project_type': project_type,
            'years_to_project_types': years_to_project_types,
            'project_type_labels': dict(LABEL_PROJECT_CHOICES),
            'insect_functional_group_chart': insect_functional_group_chart,
        }),
    })


@login_required
@permission_required(IS_GROWER_USER, raise_exception=True)
def factor_detail(request):
    """Detail view for a single factor, showing every underlying CSVImportFieldValue."""
    grower = request.user

    year = request.GET.get('year', '')
    project_type = request.GET.get('project_type', 'avalanche')
    result_type = request.GET.get('result_type', 'haney')
    depth = request.GET.get('depth', '')
    factor_name = request.GET.get('factor_name', '')

    factor_info = {}
    for _table, factors in RESULT_TYPE_FACTOR_MAPPING.get(result_type, {}).items():
        if factor_name in factors:
            factor_info = factors[factor_name]
            break

    csv_field_name = factor_info.get('field_name', '')

    field_values = CSVImportFieldValue.objects.none()
    if csv_field_name:
        try:
            year_int = int(year)
            if _uses_sample_code_grower_join(project_type, result_type):
                extra_related = [
                    'row__sample_code__used_in_application',
                    'row__sample_code__used_in_application__field',
                    'row__sample_code__used_in_application__field__farm',
                ]
                order = ('row__sample_code__code', 'row__depth', 'pk')
            else:
                extra_related = [
                    'row__site_transect__site_code__used_in_application',
                    'row__site_transect__site_code__used_in_application__field',
                    'row__site_transect__site_code__used_in_application__field__farm',
                ]
                order = ('row__site_transect__site_code__code', 'row__depth', 'pk')
            field_values = (
                _field_value_qs(grower, year_int, project_type, result_type, depth=depth)
                .filter(field_name=csv_field_name)
                .select_related(*extra_related)
                .order_by(*order)
            )
        except (ValueError, TypeError):
            pass

    rows = []
    numeric_values = []
    non_numeric_values = []
    for fv in field_values:
        row = fv.row
        if project_type == 'ignite' and row.site_transect:
            sample_code = row.site_transect.site_code.code
            transect_number = row.site_transect.transect_number
            application = row.site_transect.site_code.used_in_application
        elif row.sample_code:
            sample_code = row.sample_code.code
            transect_number = None
            application = row.sample_code.used_in_application
        else:
            sample_code = None
            transect_number = None
            application = None

        is_num = _is_numeric(fv.field_value)
        rows.append({
            'sample_code': sample_code,
            'transect_number': transect_number,
            'depth': row.depth,
            'field_value': fv.field_value,
            'is_numeric': is_num,
            'import_date': row.import_log.import_date if row.import_log else None,
            'application_id': application.pk if application else None,
            'application_code': application.submission_code if application else None,
            'date_sampled': application.date_sampled if application else None,
            'farm_field': application.field.field_name if application and application.field else None,
            'farm_name': (
                application.field.farm.name
                if application and application.field and application.field.farm else None
            ),
        })
        if fv.field_value is not None and str(fv.field_value).strip():
            if is_num:
                numeric_values.append(float(str(fv.field_value).strip()))
            else:
                non_numeric_values.append(str(fv.field_value).strip())

    if numeric_values:
        aggregate_value = sum(numeric_values) / len(numeric_values)
        aggregate_label = 'average'
        aggregate_is_numeric = True
    elif non_numeric_values:
        aggregate_value = Counter(non_numeric_values).most_common(1)[0][0]
        aggregate_label = 'most common'
        aggregate_is_numeric = False
    else:
        aggregate_value = None
        aggregate_label = None
        aggregate_is_numeric = False

    return render(request, 'grower_portal/grower/factor_detail.html', {
        'factor_name': factor_name,
        'units': factor_info.get('units', ''),
        'summary': factor_info.get('summary', ''),
        'description': factor_info.get('description', ''),
        'aggregate_value': aggregate_value,
        'aggregate_label': aggregate_label,
        'aggregate_is_numeric': aggregate_is_numeric,
        'rows': rows,
        'project_type': project_type,
        'project_type_display': dict(LABEL_PROJECT_CHOICES).get(project_type, project_type),
        'result_type': result_type,
        'result_type_display': dict(RESULT_TYPE_CHOICES).get(result_type, result_type),
        'year': year,
        'depth': depth,
    })
