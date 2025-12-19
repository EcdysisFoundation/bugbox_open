from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.http import FileResponse
from django.core.files.base import ContentFile
from django.core.paginator import Paginator

from bugbox3.core.permissions import IS_GROWERADMIN
from ...models import LabelGeneration
from ...forms.admin.label_forms import LabelGenerationForm, QuickLabelGenerationForm
from ...services.label_generator import LabelGenerator
from ...middleware import get_user_timezone
from ...constants import SAMPLE_TYPES


@login_required
@permission_required(IS_GROWERADMIN, raise_exception=True)
def label_management(request):
    """Main label generation page"""
    if request.method == 'POST':
        form_type = request.POST.get('form_type', 'detailed')
        
        if form_type == 'quick':
            quick_form = QuickLabelGenerationForm(request.POST)
            
            if quick_form.is_valid():
                project_type = quick_form.cleaned_data['project_type']
                cluster_number = quick_form.cleaned_data['cluster_number']
                year = quick_form.cleaned_data['year']
                number_of_transects = quick_form.cleaned_data['number_of_transects']
                
                if project_type == '1000_farms':
                    messages.info(request, '1000 Farms quick generation to be implemented yet...')
                    return redirect('grower_portal:label_management')
                
                try:
                    generator = LabelGenerator(
                        project_type=project_type,
                        cluster_number=cluster_number,
                        year=year,
                        sample_types=[],
                        labels_per_type=number_of_transects,
                        created_by=request.user
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
                    
                except Exception as e:
                    messages.error(request, f'Error generating quick labels: {str(e)}')
            
            form = LabelGenerationForm()
            context = {
                'quick_form': quick_form,
                'form': form,
                'avalanche_sample_types': SAMPLE_TYPES,
                'thousand_farms_sample_types': SAMPLE_TYPES,
                'user_timezone': get_user_timezone(request)
            }
            return render(request, 'grower_portal/admin/label_management.html', context)
        
        else:
            form = LabelGenerationForm(request.POST)
            
            if form.is_valid():
                project_type = form.cleaned_data['project_type']
                label_category = form.cleaned_data['label_category']
                
                if label_category == 'outer':
                    messages.info(request, 'Outer labels to be implemented....')
                    return redirect('grower_portal:label_management')
                
                # inner labels
                cluster_number = form.cleaned_data['cluster_number']
                year = form.cleaned_data['year']
                sample_types = form.cleaned_data['sample_types']
                labels_per_type = form.cleaned_data['labels_per_type']
                description = form.cleaned_data.get('description', '')
                
                try:
                    generator = LabelGenerator(
                        project_type=project_type,
                        cluster_number=cluster_number,
                        year=year,
                        sample_types=sample_types,
                        labels_per_type=labels_per_type,
                        created_by=request.user
                    )
                    
                    buffer, total_labels = generator.generate_document_with_table()
                    
                    # Save to model
                    filename = f"labels_{project_type}_{cluster_number}_{year}.docx"
                    label_generation = LabelGeneration.objects.create(
                        project_type=project_type,
                        label_category=label_category,
                        cluster_number=cluster_number,
                        year=year,
                        sample_types=sample_types,
                        labels_per_type=labels_per_type,
                        total_labels_generated=total_labels,
                        generated_by=request.user,
                        description=description,
                        transect_codes_generated=generator.generated_codes
                    )
                    
                    # Save file
                    label_generation.label_file.save(filename, ContentFile(buffer.read()), save=True)
                    
                    messages.success(
                        request,
                        f'Successfully generated {total_labels} labels! '
                        f'Generated {len(generator.generated_codes)} unique transect codes.'
                    )
                    
                    return redirect('grower_portal:label_generation_detail', generation_id=label_generation.id)
                    
                except Exception as e:
                    messages.error(request, f'Error generating labels: {str(e)}')
    else:
        form = LabelGenerationForm()
        quick_form = QuickLabelGenerationForm()
    
    context = {
        'form': form,
        'quick_form': quick_form,
        'avalanche_sample_types': SAMPLE_TYPES,
        'thousand_farms_sample_types': SAMPLE_TYPES,
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

