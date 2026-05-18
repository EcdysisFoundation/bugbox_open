"""
Admin Data Ingestion Hub
Single interface for uploading all data categories into Grower Portal
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from bugbox3.core.permissions import IS_GROWERADMIN
from bugbox3.grower_portal.constants import (
    CATEGORY_CHOICES,
    CATEGORY_DISPLAY_META,
    CATEGORY_RESULT_TYPE_MAP,
    RESULT_TYPE_CHOICES,
)
from bugbox3.grower_portal.forms.admin.data_ingestion_form import DataIngestionForm
from bugbox3.grower_portal.middleware import get_user_timezone
from bugbox3.grower_portal.models import CSVImportLog
from bugbox3.grower_portal.services.data_ingestion import build_s3_path, process_bird_csv, process_generic_csv
from bugbox3.libs.utilities import get_json_context

_RESULT_TYPE_DISPLAY = dict(RESULT_TYPE_CHOICES)


def _dispatch_ingestion(csv_import_log, uploaded_file, category: str, project_type: str, result_type: str):
    """Call the correct ingestion handler based on category."""
    if category == "birds":
        return process_bird_csv(csv_import_log, uploaded_file)
    return process_generic_csv(csv_import_log, uploaded_file, project_type, result_type)


@login_required
@permission_required(IS_GROWERADMIN, raise_exception=True)
def data_ingestion_hub(request):
    """
    Unified data ingestion page.  Handles both GET (render form + history)
    and POST (validate + ingest uploaded file).
    """
    if request.method == "POST":
        form = DataIngestionForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.cleaned_data["data_file"]
            category = form.cleaned_data["category"]
            result_type = form.cleaned_data["result_type"]
            project_type = form.cleaned_data["project_type"]
            year = form.cleaned_data["year"]
            description = form.cleaned_data.get("description", "")

            # Save file to organised S3 path
            s3_path = build_s3_path(category, result_type, year, uploaded_file.name)
            uploaded_file.seek(0)
            saved_path = default_storage.save(s3_path, ContentFile(uploaded_file.read()))

            csv_import_log = CSVImportLog.objects.create(
                filename=uploaded_file.name,
                imported_by=request.user,
                file_path=saved_path,
                description=description,
                status="pending",
                total_records=0,
                successful_records=0,
                failed_records=0,
                project_type=project_type,
                result_type=result_type,
                category=category,
            )

            uploaded_file.seek(0)
            total, successful, failed, error_log = _dispatch_ingestion(
                csv_import_log, uploaded_file, category, project_type, result_type
            )

            warnings = [e for e in error_log if "warning" in e]
            errors = [e for e in error_log if "error" in e]

            if errors and successful == 0:
                status = "failed"
            elif errors or warnings:
                status = "completed_with_errors"
            else:
                status = "completed"

            csv_import_log.status = status
            csv_import_log.total_records = total
            csv_import_log.successful_records = successful
            csv_import_log.failed_records = failed
            csv_import_log.error_log = error_log
            csv_import_log.save()

            if status == "completed":
                messages.success(
                    request,
                    f'"{uploaded_file.name}" imported successfully — '
                    f"{successful} record(s) saved. Import #{csv_import_log.id}",
                )
            elif status == "completed_with_errors":
                messages.warning(
                    request,
                    f'"{uploaded_file.name}" imported with issues — '
                    f"{successful} record(s) saved, {failed} skipped, "
                    f"{len(warnings)} warning(s). Review the import log below. "
                    f"Import #{csv_import_log.id}",
                )
            else:
                messages.error(
                    request,
                    f'"{uploaded_file.name}" could not be imported — '
                    f"0 records saved, {failed} row(s) failed. "
                    f"Review the error log. Import #{csv_import_log.id}",
                )

            return redirect("grower_portal:admin_csv_import_detail", import_id=csv_import_log.id)
    else:
        form = DataIngestionForm()

    # Import history (filterable by category)
    category_filter = request.GET.get("category", "")
    imports_qs = CSVImportLog.objects.select_related("imported_by").order_by("-import_date")
    if category_filter:
        imports_qs = imports_qs.filter(category=category_filter)

    paginator = Paginator(imports_qs, 20)
    imports = paginator.get_page(request.GET.get("page"))

    # Build category metadata list for template
    categories_meta = [
        {
            "value": value,
            "label": label,
            "icon": CATEGORY_DISPLAY_META.get(value, {}).get("icon", "fa-folder"),
            "description": CATEGORY_DISPLAY_META.get(value, {}).get("description", ""),
        }
        for value, label in CATEGORY_CHOICES
    ]

    selected_category = form["category"].value() or ""

    return render(
        request,
        "grower_portal/admin/data_ingestion.html",
        {
            "form": form,
            "imports": imports,
            "categories_meta": categories_meta,
            "category_choices": CATEGORY_CHOICES,
            "category_filter": category_filter,
            "user_timezone": get_user_timezone(request),
            "json_context": get_json_context(
                {
                    "categoryResultTypesUrl": reverse(
                        "grower_portal:admin_category_result_types"
                    ),
                    "selectedCategory": selected_category,
                }
            ),
        },
    )


@login_required
@permission_required(IS_GROWERADMIN, raise_exception=True)
def category_result_types_ajax(request):
    """
    returns result_types valid for the requested category.
    used by the frontend to populate the Data Type dropdown dynamically
    """
    category = request.GET.get("category", "")
    result_type_keys = CATEGORY_RESULT_TYPE_MAP.get(category, [])
    result_types = [
        {"value": key, "label": _RESULT_TYPE_DISPLAY.get(key, key)}
        for key in result_type_keys
    ]
    return JsonResponse({"result_types": result_types})
