from .dashboard import admin_dashboard
from .growers import grower_list, grower_detail
from .farms import farm_list, farm_detail
from .fields import field_list, field_detail
from .applications import application_list, application_detail, application_edit_redirect, application_delete
from .application_edit import (
    admin_application_edit_basic,
    admin_application_edit_management,
    admin_application_edit_transects,
    admin_application_submit
)
from .transect_codes import transect_code_list, transect_code_generate, transect_code_deactivate, transect_code_reactivate
from .csv_import import csv_upload, csv_import_list, csv_import_detail, csv_import_download, csv_import_download_error_log, csv_import_delete
from .reports import report_list, report_detail
from .label_management import (
    label_management,
    label_generation_list,
    label_generation_detail,
    label_generation_download,
    inner_label_generations_json
)

__all__ = [
    'admin_dashboard',
    'grower_list',
    'grower_detail',
    'farm_list',
    'farm_detail',
    'field_list',
    'field_detail',
    'application_list',
    'application_detail',
    'application_edit_redirect',
    'application_delete',
    'admin_application_edit_basic',
    'admin_application_edit_management',
    'admin_application_edit_transects',
    'admin_application_submit',
    'transect_code_list',
    'transect_code_generate',
    'transect_code_deactivate',
    'transect_code_reactivate',
    'csv_upload',
    'csv_import_list',
    'csv_import_detail',
    'csv_import_download',
    'csv_import_download_error_log',
    'csv_import_delete',
    'report_list',
    'report_detail',
    'label_management',
    'label_generation_list',
    'label_generation_detail',
    'label_generation_download',
    'inner_label_generations_json',
]
