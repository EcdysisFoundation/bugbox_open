from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.files.base import ContentFile
from django.core.paginator import Paginator
from django.http import FileResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from bugbox3.core.permissions import IS_GROWERADMIN

from ...constants import IGNITE_INNER_SAMPLE_TYPES, IGNITE_OUTER_SAMPLE_TYPES, SAMPLE_TYPES
from ...forms.admin.label_forms import QuickLabelGenerationForm
from ...middleware import get_user_timezone
from ...models import LabelGeneration
from ...services.label_generator import LabelGenerator


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

                            generator = LabelGenerator(
                                project_type='ignite',
                                cluster_number=cluster_number,
                                year=year,
                                sample_types=sample_types,
                                labels_per_type=1,
                                created_by=request.user,
                                label_category='outer'
                            )

                            buffer, total_labels = generator.generate_outer_labels_ignite(site_codes)
                            all_sample_types = sample_types
                        else:  # inner
                            # Filter out excluded sample types
                            sample_types = [st for st in IGNITE_INNER_SAMPLE_TYPES if st not in excluded_types]

                            if not sample_types:
                                messages.error(
                                    request, 'All sample types are excluded. Please include at least one sample type.')
                                return redirect('grower_portal:label_management')

                            generator = LabelGenerator(
                                project_type='ignite',
                                cluster_number=cluster_number,
                                year=year,
                                sample_types=sample_types,
                                labels_per_type=4,  # 4 labels per site (T1-T4)
                                created_by=request.user
                            )

                            buffer, total_labels = generator.generate_quick_labels_ignite(number_of_transects)
                            all_sample_types = sample_types

                        # Save label generation record
                        label_generation = LabelGeneration.objects.create(
                            project_type=project_type,
                            label_category=label_category,
                            cluster_number=cluster_number,
                            year=year,
                            sample_types=all_sample_types,
                            labels_per_type=4 if label_category == 'inner' else 1,
                            total_labels_generated=total_labels,
                            transect_codes_generated=(
                                generator.generated_codes
                                if label_category == 'inner'
                                else site_codes
                            ),
                            generated_by=request.user)

                        filename = f"ignite_{label_category}_{cluster_number}_{year}_labels.docx"
                        buffer.seek(0)  # Reset buffer position before saving
                        label_generation.label_file.save(filename, ContentFile(buffer.read()))

                        # Return the file for download
                        buffer.seek(0)  # Reset again for download
                        response = FileResponse(
                            buffer,
                            as_attachment=True,
                            filename=filename,
                            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                        )
                        return response

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

                        generator = LabelGenerator(
                            project_type=project_type,
                            cluster_number=cluster_number,
                            year=year,
                            sample_types=[],
                            labels_per_type=0,
                            created_by=request.user,
                            label_category='outer'
                        )

                        buffer, total_labels = generator.generate_outer_labels_avalanche(transect_codes)

                        filename = f"labels_outer_{project_type}_{cluster_number}_{year}.docx"
                        label_generation = LabelGeneration.objects.create(
                            project_type=project_type,
                            label_category='outer',
                            cluster_number=cluster_number,
                            year=year,
                            sample_types=[],
                            labels_per_type=0,
                            total_labels_generated=total_labels,
                            generated_by=request.user,
                            description=f'Outer labels generated from inner generation #{inner_generation.id}',
                            transect_codes_generated=transect_codes
                        )

                        buffer.seek(0)
                        label_generation.label_file.save(filename, ContentFile(buffer.read()), save=True)

                        buffer.seek(0)
                        response = FileResponse(
                            buffer,
                            as_attachment=True,
                            filename=filename,
                            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                        )
                        return response

                    else:
                        number_of_transects = quick_form.cleaned_data['number_of_transects']
                        excluded_types = quick_form.cleaned_data.get('excluded_sample_types', [])

                        all_sample_types = [code for code, _ in SAMPLE_TYPES if code not in excluded_types]

                        if not all_sample_types:
                            messages.error(
                                request, 'All sample types are excluded. Please include at least one sample type.')
                            return redirect('grower_portal:label_management')

                        generator = LabelGenerator(
                            project_type=project_type,
                            cluster_number=cluster_number,
                            year=year,
                            sample_types=all_sample_types,
                            labels_per_type=number_of_transects,
                            created_by=request.user,
                            label_category='inner'
                        )

                        buffer, total_labels = generator.generate_quick_labels_avalanche(number_of_transects)

                        filename = f"labels_quick_{project_type}_{cluster_number}_{year}.docx"
                        label_generation = LabelGeneration.objects.create(
                            project_type=project_type,
                            label_category='inner',
                            cluster_number=cluster_number,
                            year=year,
                            sample_types=all_sample_types,
                            labels_per_type=number_of_transects,
                            total_labels_generated=total_labels,
                            generated_by=request.user,
                            description=f'Quick generation: {number_of_transects} transects with full sample set',
                            transect_codes_generated=generator.generated_codes
                        )

                        buffer.seek(0)
                        label_generation.label_file.save(filename, ContentFile(buffer.read()), save=True)

                        buffer.seek(0)
                        response = FileResponse(
                            buffer,
                            as_attachment=True,
                            filename=filename,
                            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                        )
                        return response

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
        project_type=project_type
    ).order_by('-generated_at')[:50]

    results = []
    for gen in generations:
        transect_count = len(gen.transect_codes_generated) if gen.transect_codes_generated else 0
        results.append({
            'id': gen.id,
            'generated_at': gen.generated_at.strftime('%Y-%m-%d %H:%M'),
            'total_labels': gen.total_labels_generated,
            'transect_count': transect_count,
            'project_type_display': gen.get_project_type_display()
        })

    return JsonResponse({'generations': results})
