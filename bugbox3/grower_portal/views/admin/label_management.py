from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.http import FileResponse, JsonResponse
from django.core.files.base import ContentFile
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods

from bugbox3.core.permissions import IS_GROWERADMIN
from ...models import LabelGeneration
from ...forms.admin.label_forms import QuickLabelGenerationForm
from ...services.label_generator import LabelGenerator
from ...middleware import get_user_timezone
from ...constants import SAMPLE_TYPES


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
                
                if project_type == '1000_farms':
                    messages.info(request, '1000 Farms quick generation to be implemented yet...')
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
                        
                        label_generation.label_file.save(filename, ContentFile(buffer.read()), save=True)
                        
                        messages.success(
                            request,
                            f'Successfully generated {total_labels} outer labels for {len(transect_codes)} transects!'
                        )
                        
                        return redirect('grower_portal:label_generation_detail', generation_id=label_generation.id)
                    
                    else:
                        number_of_transects = quick_form.cleaned_data['number_of_transects']
                        
                        generator = LabelGenerator(
                            project_type=project_type,
                            cluster_number=cluster_number,
                            year=year,
                            sample_types=[],
                            labels_per_type=number_of_transects,
                            created_by=request.user,
                            label_category='inner'
                        )
                        
                        buffer, total_labels = generator.generate_quick_labels_avalanche(number_of_transects)
                        
                        all_sample_types = [code for code, _ in SAMPLE_TYPES]
                        
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
                        
                        label_generation.label_file.save(filename, ContentFile(buffer.read()), save=True)
                        
                        messages.success(
                            request,
                            f'Successfully generated {total_labels} labels for {number_of_transects} transects! '
                            f'Generated {len(generator.generated_codes)} unique transect codes.'
                        )
                        
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
    """AJAX endpoint to get inner label generations for a cluster/year"""
    cluster_number = request.GET.get('cluster', '').strip()
    year = request.GET.get('year', '').strip()
    
    if not cluster_number or not year:
        return JsonResponse({'generations': []})
    
    try:
        year_int = int(year)
    except ValueError:
        return JsonResponse({'generations': []})
    
    generations = LabelGeneration.objects.filter(
        label_category='inner',
        cluster_number=cluster_number,
        year=year_int
    ).order_by('-generated_at')[:50]
    
    results = []
    for gen in generations:
        transect_count = len(gen.transect_codes_generated) if gen.transect_codes_generated else 0
        results.append({
            'id': gen.id,
            'generated_at': gen.generated_at.strftime('%Y-%m-%d %H:%M'),
            'total_labels': gen.total_labels_generated,
            'transect_count': transect_count
        })
    
    return JsonResponse({'generations': results})

