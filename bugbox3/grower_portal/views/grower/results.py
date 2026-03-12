from collections import Counter, defaultdict
from datetime import date

from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse

from bugbox3.core.permissions import IS_GROWER_USER
from bugbox3.libs.utilities import get_json_context

from ...constants import LABEL_PROJECT_CHOICES, RESULT_TYPE_CHOICES, RESULT_TYPE_FACTOR_MAPPING
from ...forms.grower.forms import ResultsFilterForm
from ...middleware import get_user_timezone
from ...models import CSVImportFieldValue, CSVImportRow


def _field_value_filters(grower, year_int, project_type, result_type):
    """Build ORM filter kwargs scoping CSVImportFieldValue to a grower/year/project/result."""
    if project_type == 'ignite':
        prefix = 'row__site_transect__site_code__grower_mappings'
    else:
        prefix = 'row__sample_code__grower_mappings'
    return {
        f'{prefix}__grower': grower,
        f'{prefix}__year_sampled': year_int,
        'row__import_log__project_type': project_type,
        'row__import_log__result_type': result_type,
    }


def _field_value_qs(grower, year_int, project_type, result_type, depth=None):
    """Return a CSVImportFieldValue queryset with appropriate select_related."""
    filters = _field_value_filters(grower, year_int, project_type, result_type)
    if depth:
        filters['row__depth'] = depth
    related = ['row', 'row__site_transect', 'row__site_transect__site_code', 'row__import_log']
    if project_type != 'ignite':
        related.append('row__sample_code')
    return (
        CSVImportFieldValue.objects
        .filter(**filters)
        .select_related(*related)
        .distinct()
        .order_by('row', 'field_name', 'field_value')
    )


def _get_depth_options(grower, year, project_type, result_type='basic'):
    """
    Get depth options for a given year, project_type, and result_type.
    Returns a list of (value, label) tuples sorted by beginning depth, then ending depth.
    """
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
    """Check if a value can be converted to a numeric type."""
    if value is None or value == '':
        return False
    try:
        float(str(value).strip())
        return True
    except (ValueError, TypeError):
        return False


def _aggregate_field_values(field_values):
    """
    Aggregate CSVImportFieldValues with the same field_name.
    Returns average for numeric values, most common value for non-numeric.
    """
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
        numeric = [float(str(v).strip()) for v in non_empty if _is_numeric(v)]
        if numeric:
            aggregated[field_name] = sum(numeric) / len(numeric)
        else:
            non_numeric = [str(v).strip() for v in non_empty]
            aggregated[field_name] = Counter(non_numeric).most_common(1)[0][0]

    return aggregated


def _organize_results_by_mapping(field_values, result_type):
    """
    Organize aggregated field values according to RESULT_TYPE_FACTOR_MAPPING.
    Returns {table_name: [{factor_name, units, value, individual_values}]}
    """
    factor_mapping = RESULT_TYPE_FACTOR_MAPPING.get(result_type)
    if not factor_mapping:
        return {}

    aggregated_values = _aggregate_field_values(field_values)
    if not aggregated_values:
        return {}

    # Build per-row values keyed by field_name (queryset already evaluated above).
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


@login_required
@permission_required(IS_GROWER_USER, raise_exception=True)
def basic_results_ajax(request):
    """AJAX endpoint returning the Basic results tables HTML fragment."""
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
    """AJAX endpoint to get depth options based on year, project_type, and result_type."""
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
    """Grower results dashboard."""
    grower = request.user

    avalanche_year_set = set(
        CSVImportFieldValue.objects.filter(
            row__sample_code__grower_mappings__grower=grower,
            row__import_log__project_type='avalanche',
        ).order_by().values_list(
            'row__sample_code__grower_mappings__year_sampled', flat=True
        ).distinct()
    ) - {None}

    ignite_year_set = set(
        CSVImportFieldValue.objects.filter(
            row__site_transect__site_code__grower_mappings__grower=grower,
            row__import_log__project_type='ignite',
        ).order_by().values_list(
            'row__site_transect__site_code__grower_mappings__year_sampled', flat=True
        ).distinct()
    ) - {None}

    available_years = sorted(avalanche_year_set | ignite_year_set, reverse=True) or [date.today().year]

    # Build year -> available project types mapping for client-side dropdown filtering.
    years_to_project_types = {}
    for y in avalanche_year_set:
        years_to_project_types.setdefault(str(y), []).append('avalanche')
    for y in ignite_year_set:
        years_to_project_types.setdefault(str(y), []).append('ignite')

    default_year = available_years[0]
    year_str = request.GET.get('year', '')
    result_type_filter = request.GET.get('result_type', '')
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
            result_type_filter = form.cleaned_data.get('result_type', result_type_filter)
    else:
        form = ResultsFilterForm(
            initial={'year': year, 'project_type': project_type},
            available_years=available_years,
        )

    result_type_results = []
    all_depth_options = {}
    try:
        year_int = int(year)
        for rt_value, rt_display in RESULT_TYPE_CHOICES:
            rt_depth_options = _get_depth_options(grower, year, project_type, rt_value)
            all_depth_options[rt_value] = rt_depth_options
            field_values = _field_value_qs(
                grower, year_int, project_type, rt_value,
                depth=depth,
            )
            result_type_results.append({
                'result_type': rt_value,
                'display': rt_display,
                'organized_results': _organize_results_by_mapping(field_values, rt_value),
                'depth_options': rt_depth_options,
            })
    except (ValueError, TypeError):
        pass

    depth_options = all_depth_options.get('basic', [])

    return render(request, 'grower_portal/grower/results.html', {
        'form': form,
        'result_type_results': result_type_results,
        'depth_options': depth_options,
        'year': year,
        'project_type': project_type,
        'project_type_display': dict(LABEL_PROJECT_CHOICES).get(project_type, project_type),
        'result_type_filter': result_type_filter,
        'depth': depth,
        'user_timezone': get_user_timezone(request),
        'json_context': get_json_context({
            'factor_detail_url': reverse('grower_portal:factor_detail'),
            'basic_results_url': reverse('grower_portal:basic_results_ajax'),
            'year': year,
            'project_type': project_type,
            'result_type_filter': result_type_filter,
            'years_to_project_types': years_to_project_types,
            'project_type_labels': dict(LABEL_PROJECT_CHOICES),
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
            if project_type == 'ignite':
                extra_related = [
                    'row__site_transect__site_code__used_in_application',
                    'row__site_transect__site_code__used_in_application__field',
                    'row__site_transect__site_code__used_in_application__field__farm',
                ]
                order = ('row__site_transect__site_code__code', 'row__depth', 'pk')
            else:
                extra_related = [
                    'row__sample_code__used_in_application',
                    'row__sample_code__used_in_application__field',
                    'row__sample_code__used_in_application__field__farm',
                ]
                order = ('row__sample_code__code', 'row__depth', 'pk')
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
        else:
            sample_code = row.sample_code.code if row.sample_code else None
            transect_number = None
            application = row.sample_code.used_in_application if row.sample_code else None

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
