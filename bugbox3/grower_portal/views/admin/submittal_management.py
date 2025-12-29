from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.http import FileResponse, HttpResponse
from io import BytesIO
import zipfile

from bugbox3.core.permissions import IS_GROWERADMIN
from ...forms.admin.submittal_forms import SubmittalFormGenerationForm
from ...services.submittal_generator import SubmittalFormGenerator


@login_required
@permission_required(IS_GROWERADMIN, raise_exception=True)
def generate_submittal_form(request):
    """
    generate submittal forms based on cluster number and year.
    """
    if request.method == 'POST':
        form = SubmittalFormGenerationForm(request.POST)
        
        if form.is_valid():
            cluster = form.cleaned_data['cluster_number']
            year = form.cleaned_data['year']
            generate_soil = form.cleaned_data.get('generate_soil', True)
            generate_plant = form.cleaned_data.get('generate_plant', True)
            
            try:
                generator = SubmittalFormGenerator(cluster, year)
                files = generator.generate_submittal_form(
                    generate_soil=generate_soil,
                    generate_plant=generate_plant
                )
                
                if len(files) == 1:
                    buffer, filename = files[0]
                    response = FileResponse(
                        buffer,
                        as_attachment=True,
                        filename=filename
                    )
                    response['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                    
                    messages.success(
                        request,
                        f'Submittal form generated successfully for cluster {cluster} ({year})'
                    )
                    
                    return response
                
                # zip for multiple files
                zip_buffer = BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    for buffer, filename in files:
                        buffer.seek(0)
                        zip_file.writestr(filename, buffer.read())
                
                zip_buffer.seek(0)
                zip_filename = f"Submittal_Forms_{cluster}_{year}.zip"
                
                response = HttpResponse(
                    zip_buffer.read(),
                    content_type='application/zip'
                )
                response['Content-Disposition'] = f'attachment; filename="{zip_filename}"'
                
                messages.success(
                    request,
                    f'Submittal forms generated successfully for cluster {cluster} ({year})'
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
        'page_title': 'Generate Submittal Form'
    }
    
    return render(request, 'grower_portal/admin/submittal_form_generator.html', context)



