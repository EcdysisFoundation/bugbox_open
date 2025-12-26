from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.http import FileResponse

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
            
            try:
                generator = SubmittalFormGenerator(cluster, year)
                buffer, filename = generator.generate_submittal_form()
                
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



