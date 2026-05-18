import zipfile
from io import BytesIO

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.http import FileResponse, HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

from bugbox3.core.permissions import IS_GROWERADMIN

from ...constants import LABEL_PROJECT_CHOICES
from ...forms.admin.submittal_forms import SubmittalFormGenerationForm
from ...models import LabelGeneration
from ...services.submittal_generator import SubmittalFormGenerator


@login_required
@permission_required(IS_GROWERADMIN, raise_exception=True)
@require_GET
def submittal_label_generations_json(request):
    """
    List ready inner label generations and codes for submittal form generation
    """
    project_type = request.GET.get('project_type', '').strip()
    cluster_number = request.GET.get('cluster', '').strip()
    year_raw = request.GET.get('year', '').strip()

    if not project_type or not cluster_number or not year_raw:
        return JsonResponse({'generations': []})

    try:
        year = int(year_raw)
    except ValueError:
        return JsonResponse({'generations': []})

    generations = LabelGeneration.objects.filter(
        project_type=project_type,
        cluster_number=cluster_number,
        year=year,
        label_category='inner',
        status='ready',
    ).order_by('-generated_at')[:50]

    project_labels = dict(LABEL_PROJECT_CHOICES)
    results = []
    for gen in generations:
        if (gen.generation_params or {}).get('ignite_forage_supplement'):
            continue
        codes = [str(c).strip() for c in (gen.transect_codes_generated or []) if str(c).strip()]
        if not codes:
            continue
        sample_types = gen.sample_types or []
        results.append({
            'id': gen.id,
            'generated_at': gen.generated_at.strftime('%Y-%m-%d %H:%M'),
            'code_count': len(codes),
            'codes': codes,
            'sample_types': sample_types,
            'has_forage': 'forage' in sample_types,
            'project_type_display': project_labels.get(gen.project_type, gen.project_type),
            'total_labels': gen.total_labels_generated,
        })

    return JsonResponse({'generations': results})


@login_required
@permission_required(IS_GROWERADMIN, raise_exception=True)
def generate_submittal_form(request):
    """
    Generate submittal forms for a chosen project, label batch, and selected codes.
    """
    if request.method == 'POST':
        form = SubmittalFormGenerationForm(request.POST)

        if form.is_valid():
            cluster = form.cleaned_data['cluster_number']
            year = form.cleaned_data['year']
            project_type = form.cleaned_data['project_type']
            label_gen = form.cleaned_data['label_generation']
            selected_codes = form.cleaned_data['selected_codes_ordered']
            generate_soil = form.cleaned_data.get('generate_soil', True)
            generate_plant = form.cleaned_data.get('generate_plant', True)

            try:
                generator = SubmittalFormGenerator(
                    cluster,
                    year,
                    project_type,
                    label_gen,
                    selected_codes,
                )
                files = generator.generate_submittal_form(
                    generate_soil=generate_soil,
                    generate_plant=generate_plant,
                )

                prefix = f"{project_type}_{cluster}_{year}"

                if len(files) == 1:
                    buffer, filename = files[0]
                    response = FileResponse(
                        buffer,
                        as_attachment=True,
                        filename=filename,
                    )
                    response['Content-Type'] = (
                        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                    )
                    messages.success(
                        request,
                        f'Submittal form generated for {project_type} cluster {cluster} ({year}), '
                        f'{len(selected_codes)} code(s).',
                    )
                    return response

                zip_buffer = BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    for buffer, filename in files:
                        buffer.seek(0)
                        zip_file.writestr(filename, buffer.read())

                zip_buffer.seek(0)
                zip_filename = f"Submittal_Forms_{prefix}.zip"

                response = HttpResponse(
                    zip_buffer.read(),
                    content_type='application/zip',
                )
                response['Content-Disposition'] = f'attachment; filename="{zip_filename}"'

                messages.success(
                    request,
                    f'Submittal forms generated for {project_type} cluster {cluster} ({year}), '
                    f'{len(selected_codes)} code(s).',
                )
                return response

            except ValueError as e:
                messages.error(request, f'Error generating submittal form: {str(e)}')
            except Exception as e:
                messages.error(request, f'Unexpected error: {str(e)}')
                if hasattr(request, 'debug') or request.META.get('DEBUG'):
                    raise
    else:
        form = SubmittalFormGenerationForm()

    context = {
        'form': form,
        'page_title': 'Generate Submittal Form',
    }

    return render(request, 'grower_portal/admin/submittal_form_generator.html', context)
