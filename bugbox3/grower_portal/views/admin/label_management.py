from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.db import transaction
from django.http import FileResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from bugbox3.core.permissions import IS_GROWERADMIN

from ...constants import IGNITE_INNER_SAMPLE_TYPES, IGNITE_OUTER_SAMPLE_TYPES, SAMPLE_TYPES
from ...forms.admin.label_forms import QuickLabelGenerationForm
from ...middleware import get_user_timezone
from ...models import LabelGeneration, SampleCode
from ...tasks import generate_labels_async


def _enqueue_label_generation_task(label_generation: LabelGeneration) -> None:
    """
    Queue Celery after the HTTP requests DB transaction commits
    """
    pk = label_generation.pk

    def enqueue():
        task = generate_labels_async.delay(pk)
        LabelGeneration.objects.filter(pk=pk).update(task_id=task.id)

    transaction.on_commit(enqueue)


@login_required
@permission_required(IS_GROWERADMIN, raise_exception=True)
def label_management(request):
    """Main label generation page"""
    if request.method == 'POST':
        form_type = request.POST.get('form_type', 'quick')

        if form_type == 'quick':
            quick_form = QuickLabelGenerationForm(request.POST)

            if quick_form.is_valid():
                project_type = quick_form.cleaned_data['project_type']
                label_category = quick_form.cleaned_data.get('label_category', 'inner')
                cluster_number = quick_form.cleaned_data['cluster_number']
                year = quick_form.cleaned_data['year']

                if project_type == 'ignite':
                    number_of_transects = quick_form.cleaned_data['number_of_transects']
                    excluded_types = quick_form.cleaned_data.get('excluded_sample_types', [])

                    try:
                        if label_category == 'outer':
                            inner_label_generation_id = quick_form.cleaned_data['inner_label_generation']
                            inner_generation = LabelGeneration.objects.get(
                                id=inner_label_generation_id,
                                label_category='inner',
                                cluster_number=cluster_number,
                                year=year
                            )

                            site_codes = inner_generation.transect_codes_generated or []

                            if not site_codes:
                                messages.error(request, 'Selected inner label generation has no site codes.')
                                return redirect('grower_portal:label_management')

                            # Filter out excluded sample types
                            sample_types = [st for st in IGNITE_OUTER_SAMPLE_TYPES if st not in excluded_types]

                            if not sample_types:
                                messages.error(
                                    request, 'All sample types are excluded. Please include at least one sample type.')
                                return redirect('grower_portal:label_management')

                            label_generation = LabelGeneration.objects.create(
                                project_type=project_type,
                                label_category='outer',
                                cluster_number=cluster_number,
                                year=year,
                                sample_types=sample_types,
                                labels_per_type=1,
                                total_labels_generated=0,
                                generated_by=request.user,
                                transect_codes_generated=site_codes,
                                generation_params={
                                    'sample_types': sample_types,
                                    'labels_per_type': 1,
                                    'site_codes': site_codes,
                                },
                            )
                            _enqueue_label_generation_task(label_generation)

                            messages.success(request, 'Ignite outer labels queued for generation.')
                            return redirect('grower_portal:label_generation_detail', generation_id=label_generation.id)
                        else:  # inner
                            # Filter out excluded sample types
                            sample_types = [st for st in IGNITE_INNER_SAMPLE_TYPES if st not in excluded_types]

                            if not sample_types:
                                messages.error(
                                    request, 'All sample types are excluded. Please include at least one sample type.')
                                return redirect('grower_portal:label_management')

                            include_forage = bool(quick_form.cleaned_data.get('include_forage_labels'))
                            if include_forage:
                                sample_types = list(sample_types) + ['forage']

                            label_generation = LabelGeneration.objects.create(
                                project_type=project_type,
                                label_category='inner',
                                cluster_number=cluster_number,
                                year=year,
                                sample_types=sample_types,
                                labels_per_type=4,
                                total_labels_generated=0,
                                generated_by=request.user,
                                transect_codes_generated=[],
                                generation_params={
                                    'number_of_transects': number_of_transects,
                                    'sample_types': sample_types,
                                    'labels_per_type': 4,
                                    'include_forage_labels': include_forage,
                                },
                            )
                            _enqueue_label_generation_task(label_generation)

                            messages.success(request, 'Ignite inner labels queued for generation.')
                            return redirect('grower_portal:label_generation_detail', generation_id=label_generation.id)

                    except Exception as e:
                        messages.error(request, f'Error generating Ignite labels: {str(e)}')
                        return redirect('grower_portal:label_management')

                try:
                    if label_category == 'outer':
                        inner_label_generation_id = quick_form.cleaned_data['inner_label_generation']
                        inner_generation = LabelGeneration.objects.get(
                            id=inner_label_generation_id,
                            label_category='inner',
                            cluster_number=cluster_number,
                            year=year
                        )

                        transect_codes = inner_generation.transect_codes_generated or []

                        if not transect_codes:
                            messages.error(request, 'Selected inner label generation has no transect codes.')
                            return redirect('grower_portal:label_management')

                        label_generation = LabelGeneration.objects.create(
                            project_type=project_type,
                            label_category='outer',
                            cluster_number=cluster_number,
                            year=year,
                            sample_types=[],
                            labels_per_type=0,
                            total_labels_generated=0,
                            generated_by=request.user,
                            description=f'Outer labels generated from inner generation #{inner_generation.id}',
                            transect_codes_generated=transect_codes,
                            generation_params={
                                'transect_codes': transect_codes,
                                'labels_per_type': 0,
                                'sample_types': [],
                            },
                        )
                        _enqueue_label_generation_task(label_generation)

                        messages.success(request, 'Outer labels queued for generation.')
                        return redirect('grower_portal:label_generation_detail', generation_id=label_generation.id)

                    else:
                        number_of_transects = quick_form.cleaned_data['number_of_transects']
                        excluded_types = quick_form.cleaned_data.get('excluded_sample_types', [])

                        all_sample_types = [code for code, _ in SAMPLE_TYPES if code not in excluded_types]

                        if not all_sample_types:
                            messages.error(
                                request, 'All sample types are excluded. Please include at least one sample type.')
                            return redirect('grower_portal:label_management')

                        label_generation = LabelGeneration.objects.create(
                            project_type=project_type,
                            label_category='inner',
                            cluster_number=cluster_number,
                            year=year,
                            sample_types=all_sample_types,
                            labels_per_type=number_of_transects,
                            total_labels_generated=0,
                            generated_by=request.user,
                            description=f'Quick generation: {number_of_transects} transects with full sample set',
                            transect_codes_generated=[],
                            generation_params={
                                'number_of_transects': number_of_transects,
                                'sample_types': all_sample_types,
                                'labels_per_type': number_of_transects,
                            },
                        )
                        _enqueue_label_generation_task(label_generation)

                        messages.success(request, 'Inner labels queued for generation.')
                        return redirect('grower_portal:label_generation_detail', generation_id=label_generation.id)

                except LabelGeneration.DoesNotExist:
                    messages.error(request, 'Selected inner label generation not found.')
                except Exception as e:
                    messages.error(request, f'Error generating quick labels: {str(e)}')

            context = {
                'quick_form': quick_form,
                'user_timezone': get_user_timezone(request)
            }
            return render(request, 'grower_portal/admin/label_management.html', context)
    else:
        quick_form = QuickLabelGenerationForm()

    context = {
        'quick_form': quick_form,
        'user_timezone': get_user_timezone(request)
    }

    return render(request, 'grower_portal/admin/label_management.html', context)


@login_required
@permission_required(IS_GROWERADMIN, raise_exception=True)
def label_generation_list(request):
    """List all label generation history"""
    generations_queryset = LabelGeneration.objects.select_related('generated_by').order_by('-generated_at')

    paginator = Paginator(generations_queryset, 20)
    page_number = request.GET.get('page')
    generations = paginator.get_page(page_number)

    context = {
        'generations': generations,
        'user_timezone': get_user_timezone(request)
    }

    return render(request, 'grower_portal/admin/label_generation_list.html', context)


@login_required
@permission_required(IS_GROWERADMIN, raise_exception=True)
def label_generation_detail(request, generation_id):
    """View details of a label generation"""
    generation = get_object_or_404(
        LabelGeneration.objects.select_related('generated_by'),
        id=generation_id
    )

    context = {
        'generation': generation,
        'user_timezone': get_user_timezone(request)
    }

    return render(request, 'grower_portal/admin/label_generation_detail.html', context)


@login_required
@permission_required(IS_GROWERADMIN, raise_exception=True)
def label_generation_download(request, generation_id):
    """Download generated label document"""
    generation = get_object_or_404(LabelGeneration, id=generation_id)

    if generation.status != 'ready':
        if generation.status == 'failed':
            messages.error(request, f'Label generation failed: {generation.error_message}')
        else:
            messages.info(request, 'Labels are still generating. Please try again in a moment.')
        return redirect('grower_portal:label_generation_detail', generation_id=generation.id)

    if not generation.label_file:
        messages.error(request, 'Label file not found.')
        return redirect('grower_portal:label_generation_list')

    response = FileResponse(
        generation.label_file.open('rb'),
        content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )
    response['Content-Disposition'] = f'attachment; filename="{generation.label_file.name.split("/")[-1]}"'

    return response


@login_required
@permission_required(IS_GROWERADMIN, raise_exception=True)
def label_generation_delete(request, generation_id):
    """
    Delete a label generation record. For inner generations, also removes the
    SampleCode rows created for that batch (listed in transect_codes_generated)
    so codes can be generated again, unless any code is in use or mapped to a grower.
    Ignite Forage-only supplement rows reuse codes from an earlier batch; deleting those
    does not remove SampleCode rows. Outer generations only remove the history row and stored file.
    """
    generation = get_object_or_404(
        LabelGeneration.objects.select_related('generated_by'),
        id=generation_id,
    )

    if request.method == 'POST':
        try:
            was_inner = generation.label_category == 'inner'
            with transaction.atomic():
                raw_codes = generation.transect_codes_generated or []
                code_strings = [str(c).strip() for c in raw_codes if str(c).strip()]

                params = generation.generation_params or {}
                skip_sample_code_delete = bool(params.get('ignite_forage_supplement'))

                if generation.label_category == 'inner' and code_strings and not skip_sample_code_delete:
                    blocked = []
                    for code_str in code_strings:
                        try:
                            sc = SampleCode.objects.select_for_update().get(code=code_str)
                        except SampleCode.DoesNotExist:
                            continue
                        if (
                            sc.is_used
                            or sc.used_in_application_id
                            or sc.grower_mappings.exists()
                        ):
                            blocked.append(code_str)

                    if blocked:
                        messages.error(
                            request,
                            'Cannot delete this inner label generation: the following sample codes '
                            'are in use or assigned to growers: '
                            + ', '.join(blocked[:20])
                            + ('…' if len(blocked) > 20 else '')
                            + ' Remove those assignments first, then try again.',
                        )
                        return redirect('grower_portal:label_generation_list')

                    SampleCode.objects.filter(code__in=code_strings).delete()

                if generation.label_file:
                    generation.label_file.delete(save=False)
                generation.delete()

            messages.success(
                request,
                'Label generation deleted.'
                + (
                    ' Associated sample codes were removed and can be generated again.'
                    if was_inner and code_strings and not skip_sample_code_delete
                    else ''
                ),
            )
        except Exception as e:
            messages.error(request, f'Could not delete label generation: {e}')
        return redirect('grower_portal:label_generation_list')

    context = {
        'generation': generation,
        'user_timezone': get_user_timezone(request),
    }
    return render(request, 'grower_portal/admin/label_generation_delete.html', context)


@login_required
@permission_required(IS_GROWERADMIN, raise_exception=True)
@require_POST
def label_regenerate_quick_avalanche(request, generation_id):
    """
    Re-queue label generation using codes already stored on the LabelGeneration row
    (rebuilds the Word file with current template fill logic; no new SampleCode rows).
    Applies to Avalanche or Ignite, inner or outer, whenever codes are stored.
    """
    generation = get_object_or_404(
        LabelGeneration.objects.select_related('generated_by'),
        id=generation_id,
    )

    codes = list(generation.transect_codes_generated or [])
    if not codes:
        messages.error(
            request,
            'This generation has no stored codes to reuse.',
        )
        return redirect('grower_portal:label_generation_detail', generation_id=generation.id)

    if generation.status in ('queued', 'processing'):
        messages.warning(
            request,
            'This generation is already queued or processing. Wait for it to finish.',
        )
        return redirect('grower_portal:label_generation_detail', generation_id=generation.id)

    with transaction.atomic():
        gen = LabelGeneration.objects.select_for_update().get(pk=generation_id)
        params = dict(gen.generation_params or {})
        params['reuse_transect_codes'] = True
        gen.generation_params = params
        gen.status = 'queued'
        gen.error_message = ''
        gen.save(update_fields=['generation_params', 'status', 'error_message'])

    _enqueue_label_generation_task(gen)

    messages.success(
        request,
        'Regeneration has been queued. The same stored codes will be used with the '
        'current label logic and templates. Refresh this page in a moment, then download the file.',
    )
    return redirect('grower_portal:label_generation_detail', generation_id=generation.id)


@login_required
@permission_required(IS_GROWERADMIN, raise_exception=True)
@require_POST
def label_ignite_forage_supplement(request, generation_id):
    """
    Queue a new Ignite inner label generation that contains only Forage labels (T1-T4 per site),
    reusing the site codes from an existing inner batch. does not create new SampleCode rows.
    """
    source = get_object_or_404(
        LabelGeneration.objects.select_related('generated_by'),
        id=generation_id,
    )

    if source.project_type != 'ignite' or source.label_category != 'inner':
        messages.error(
            request,
            'Forage-only supplement is only available for Ignite inner label generations.',
        )
        return redirect('grower_portal:label_generation_detail', generation_id=source.id)

    codes = list(source.transect_codes_generated or [])
    if not codes:
        messages.error(
            request,
            'This generation has no stored site codes to reuse.',
        )
        return redirect('grower_portal:label_generation_detail', generation_id=source.id)

    sample_types = source.sample_types or []
    if 'forage' in sample_types:
        messages.info(
            request,
            'This batch already included Forage in its sample types. Use Regenerate on this row '
            'for an updated full document, or open Label Management to generate a new inner batch.',
        )
        return redirect('grower_portal:label_generation_detail', generation_id=source.id)

    if source.status in ('queued', 'processing'):
        messages.warning(
            request,
            'Wait until this generation has finished processing, then try again.',
        )
        return redirect('grower_portal:label_generation_detail', generation_id=source.id)

    n = len(codes)
    child = LabelGeneration.objects.create(
        project_type='ignite',
        label_category='inner',
        cluster_number=source.cluster_number,
        year=source.year,
        sample_types=['forage'],
        labels_per_type=4,
        total_labels_generated=0,
        generated_by=request.user,
        description=(
            f'Ignite inner Forage-only labels (same {n} site code(s) as generation #{source.id}).'
        ),
        transect_codes_generated=list(codes),
        generation_params={
            'reuse_transect_codes': True,
            'number_of_transects': n,
            'sample_types': ['forage'],
            'labels_per_type': 4,
            'ignite_forage_supplement': True,
            'ignite_forage_supplement_source_generation_id': source.id,
        },
    )
    _enqueue_label_generation_task(child)

    messages.success(
        request,
        'A Forage-only label document has been queued using the same site codes (T1-T4 per site). '
        'Open the new generation when it is ready, then download the Word file.',
    )
    return redirect('grower_portal:label_generation_detail', generation_id=child.id)


@login_required
@permission_required(IS_GROWERADMIN, raise_exception=True)
@require_http_methods(["GET"])
def inner_label_generations_json(request):
    """endpoint to get inner label generations for a cluster/year/project"""
    cluster_number = request.GET.get('cluster', '').strip()
    year = request.GET.get('year', '').strip()
    project_type = request.GET.get('project_type', '').strip()

    if not cluster_number or not year or not project_type:
        return JsonResponse({'generations': []})

    try:
        year_int = int(year)
    except ValueError:
        return JsonResponse({'generations': []})

    generations = LabelGeneration.objects.filter(
        label_category='inner',
        cluster_number=cluster_number,
        year=year_int,
        project_type=project_type,
        status='ready',
    ).order_by('-generated_at')[:50]

    results = []
    for gen in generations:
        if (gen.generation_params or {}).get('ignite_forage_supplement'):
            continue
        transect_count = len(gen.transect_codes_generated) if gen.transect_codes_generated else 0
        results.append({
            'id': gen.id,
            'generated_at': gen.generated_at.strftime('%Y-%m-%d %H:%M'),
            'total_labels': gen.total_labels_generated,
            'transect_count': transect_count,
            'project_type_display': gen.get_project_type_display()
        })

    return JsonResponse({'generations': results})
