import csv
import io
import json

import pandas as pd
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.paginator import Paginator
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from bugbox3.core.permissions import IS_GROWERADMIN

from ...constants import CSV_IMPORT_SCHEMAS
from ...forms.admin.forms import CSVUploadForm
from ...middleware import get_user_timezone
from ...models import CSVImportFieldValue, CSVImportLog, SampleCode

TRANSECT_CODE_COLUMN_PREFIX = 'Sample ID'


def _get_transect_codes(row):
    transect_codes = set()
    for name, value in row.items():
        if name.startswith(TRANSECT_CODE_COLUMN_PREFIX) and value.strip():
            transect_codes.add(value)
    return list(transect_codes)


def _add_to_error_log(error_log, row_number, row, message):
    """Helper function to log errors with consistent formatting."""
    error_log.append({
        "row_number": row_number,
        "row_data": row,
        "error": message
    })


def _validate_sample_code(row_number, row, error_log):
    transect_codes = _get_transect_codes(row)

    if not transect_codes:
        _add_to_error_log(error_log, row_number, row, 'Row is missing transect code')
        return None

    if len(transect_codes) > 1:
        _add_to_error_log(error_log, row_number, row, f'Row has multiple transect codes: {transect_codes}')
        return None

    transect_code = transect_codes[0]

    try:
        sample_code_object = SampleCode.objects.get(code=transect_code)
    except SampleCode.DoesNotExist:
        _add_to_error_log(error_log, row_number, row, f'Transect code does not exist: {transect_code}')
        return None

    if not sample_code_object.is_active:
        _add_to_error_log(error_log, row_number, row, f'Transect code is inactive: {transect_code}')
        return None

    if not sample_code_object.used_in_application:
        _add_to_error_log(error_log, row_number, row, f'Transect code is not used in an application: {transect_code}')
        return None

    return sample_code_object


def _process_csv_file(csv_import_log, csv_file):
    csv_file.seek(0)
    content = csv_file.read()
    if isinstance(content, bytes):
        content = content.decode('utf-8-sig')

    csv_reader = csv.DictReader(io.StringIO(content))
    successful_count = 0
    failed_count = 0
    error_log = []
    validated_field_values = []

    for i, row in enumerate(csv_reader):
        try:

            sample_code_object = _validate_sample_code(
                i, row, error_log
            )

            if not sample_code_object:
                failed_count += 1
                continue

            for field_name, field_value in row.items():
                validated_field_values.append(CSVImportFieldValue(
                    import_log=csv_import_log,
                    sample_code=sample_code_object,
                    field_name=field_name,
                    field_value=field_value,
                    row_number=i
                ))
            successful_count += 1
        except Exception as e:
            failed_count += 1
            _add_to_error_log(error_log, i, row, f'Unexpected error: {e}')
            continue

    # Only save validated field values if there are no errors
    if not error_log:
        CSVImportFieldValue.objects.bulk_create(validated_field_values)

    return successful_count + failed_count, successful_count, failed_count, error_log


@login_required
@permission_required(IS_GROWERADMIN, raise_exception=True)
def csv_upload(request):
    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = form.cleaned_data['csv_file']
            description = form.cleaned_data.get('description', '')

            file_path = f'csv_imports/{csv_file.name}'
            csv_file.seek(0)
            saved_path = default_storage.save(file_path, ContentFile(csv_file.read()))

            csv_import_log = CSVImportLog.objects.create(
                filename=csv_file.name,
                imported_by=request.user,
                file_path=saved_path,
                description=description,
                status='pending',
                total_records=0,
                successful_records=0,
                failed_records=0,
            )

            total, successful, failed, error_log = _process_csv_file(csv_import_log, csv_file)

            csv_import_log.status = 'completed' if not error_log else 'failed'
            csv_import_log.total_records = total
            csv_import_log.successful_records = successful
            csv_import_log.failed_records = failed
            csv_import_log.error_log = error_log
            csv_import_log.save()

            if not error_log:
                messages.success(
                    request,
                    f'CSV file "{csv_file.name}" uploaded successfully. Import log ID: {csv_import_log.id}'
                )
            else:
                messages.error(
                    request,
                    f'CSV file "{csv_file.name}" contains errors. '
                    'File has been saved but not processed. '
                    'Please correct the errors and try again. '
                    f'Import log ID: {
                        csv_import_log.id}')

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

    pretty_error_log = []
    for obj in import_log.error_log:
        pretty = json.dumps(obj.get('row_data', ''), indent=4)
        pretty_error_log.append({
            "error": obj.get('error', ''),
            "row_number": obj.get('row_number', ''),
            "row_data": pretty
        })

    # Format JSON before sending to template
    context = {
        'import_log': import_log,
        'pretty_error_log': pretty_error_log,
        'user_timezone': get_user_timezone(request)
    }

    return render(request, 'grower_portal/admin/csv_import_detail.html', context)


@login_required
@permission_required(IS_GROWERADMIN, raise_exception=True)
def csv_import_download(request, import_id):
    """Download the CSV file associated with an import log."""
    import_log = get_object_or_404(CSVImportLog, id=import_id)

    if not import_log.file_path:
        raise Http404("File not found for this import log")
    try:
        with default_storage.open(import_log.file_path, 'rb') as file:
            file_content = file.read()

        response = HttpResponse(file_content, content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{import_log.filename}"'
        return response
    except Exception:
        raise Http404("File could not be retrieved")


@login_required
@permission_required(IS_GROWERADMIN, raise_exception=True)
def csv_import_download_error_log(request, import_id):
    """Download the error log as a CSV file."""
    import_log = get_object_or_404(CSVImportLog, id=import_id)

    if not import_log.error_log:
        raise Http404("No error log found for this import")

    error_log_df = pd.DataFrame(import_log.error_log)
    error_log_df = error_log_df.reindex(columns=['row_number', 'error', 'row_data'])

    # Create HTTP response
    response = HttpResponse(error_log_df.to_csv(index=False), content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="ERROR_LOG_{import_log.filename}"'
    return response


@login_required
@permission_required(IS_GROWERADMIN, raise_exception=True)
def csv_import_delete(request, import_id):
    """Download the CSV file associated with an import log."""
    import_log = get_object_or_404(CSVImportLog, id=import_id)

    import_log_filename = import_log.filename
    import_log_id = import_log.id

    # Delete assoociated field value records, source file, and import log record
    try:
        default_storage.delete(import_log.file_path)
    except Exception as e:
        raise RuntimeError(f"Error deleting import log file: {e}")

    CSVImportFieldValue.objects.filter(import_log=import_log).delete()
    import_log.delete()

    messages.success(request, f'Import log {import_log_filename} (ID: {import_log_id}) has been deleted.')
    return redirect('grower_portal:admin_csv_import_list')
