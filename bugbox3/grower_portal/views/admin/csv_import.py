from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os

from bugbox3.core.permissions import IS_GROWERADMIN
from ...models import CSVImportLog
from ...forms.admin.forms import CSVUploadForm
from ...middleware import get_user_timezone
from ...constants import CSV_IMPORT_SCHEMAS


@login_required
@permission_required(IS_GROWERADMIN, raise_exception=True)
def csv_upload(request):
    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = form.cleaned_data['csv_file']
            description = form.cleaned_data.get('description', '')
            
            file_path = f'csv_imports/{csv_file.name}'
            saved_path = default_storage.save(file_path, ContentFile(csv_file.read()))
            
            csv_import_log = CSVImportLog.objects.create(
                filename=csv_file.name,
                imported_by=request.user,
                status='pending',
                total_records=0,
                successful_records=0,
                failed_records=0,
                error_log=f'File saved to: {saved_path}\n\nDescription: {description}'
            )
            
            messages.success(
                request,
                f'CSV file "{csv_file.name}" uploaded successfully. Import log ID: {csv_import_log.id}'
            )
            
            return redirect('grower_portal:admin_csv_import_detail', import_id=csv_import_log.id)
    else:
        form = CSVUploadForm()
    
    context = {
        'form': form,
        'user_timezone': get_user_timezone(request),
        'csv_import_schemas': CSV_IMPORT_SCHEMAS,
    }
    
    return render(request, 'grower_portal/admin/csv_upload.html', context)


@login_required
@permission_required(IS_GROWERADMIN, raise_exception=True)
def csv_import_list(request):
    imports_queryset = CSVImportLog.objects.select_related('imported_by').order_by('-import_date')
    
    paginator = Paginator(imports_queryset, 20)
    page_number = request.GET.get('page')
    imports = paginator.get_page(page_number)
    
    context = {
        'imports': imports,
        'user_timezone': get_user_timezone(request)
    }
    
    return render(request, 'grower_portal/admin/csv_import_list.html', context)


@login_required
@permission_required(IS_GROWERADMIN, raise_exception=True)
def csv_import_detail(request, import_id):
    import_log = get_object_or_404(
        CSVImportLog.objects.select_related('imported_by'),
        id=import_id
    )
    
    context = {
        'import_log': import_log,
        'user_timezone': get_user_timezone(request)
    }
    
    return render(request, 'grower_portal/admin/csv_import_detail.html', context)

