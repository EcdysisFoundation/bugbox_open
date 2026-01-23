"""
Administrator URLs for Grower Portal (is_groweradmin)
"""
from django.urls import path

from ..views.admin import (
    admin_application_complete,
    admin_application_create_start,
    admin_application_create_step1,
    admin_application_create_step2,
    admin_application_create_step3,
    admin_application_create_step4,
    admin_application_edit_basic,
    admin_application_edit_management,
    admin_application_edit_transects,
    admin_application_submit,
    admin_dashboard,
    application_delete,
    application_detail,
    application_edit_redirect,
    application_list,
    csv_import_delete,
    csv_import_detail,
    csv_import_download,
    csv_import_download_error_log,
    csv_import_list,
    csv_upload,
    farm_detail,
    farm_list,
    field_detail,
    field_list,
    grower_detail,
    grower_list,
    inner_label_generations_json,
    label_generation_detail,
    label_generation_download,
    label_generation_list,
    label_management,
    link_application_to_grower,
    report_detail,
    report_list,
    transect_code_deactivate,
    transect_code_generate,
    transect_code_list,
    transect_code_reactivate,
)
from ..views.admin.submittal_management import generate_submittal_form

urlpatterns = [
    path('dashboard/', admin_dashboard, name='admin_dashboard'),

    path('growers/', grower_list, name='admin_grower_list'),
    path('growers/<int:grower_id>/', grower_detail, name='admin_grower_detail'),

    path('farms/', farm_list, name='admin_farm_list'),
    path('farms/<int:farm_id>/', farm_detail, name='admin_farm_detail'),

    path('fields/', field_list, name='admin_field_list'),
    path('fields/<int:field_id>/', field_detail, name='admin_field_detail'),

    path('applications/', application_list, name='admin_application_list'),
    path(
        'applications/create/',
        admin_application_create_start,
        name='admin_application_create_start'
    ),
    path(
        'applications/create/<int:application_id>/step1/',
        admin_application_create_step1,
        name='admin_application_create_step1'
    ),
    path(
        'applications/create/<int:application_id>/step2/',
        admin_application_create_step2,
        name='admin_application_create_step2'
    ),
    path(
        'applications/create/<int:application_id>/step3/',
        admin_application_create_step3,
        name='admin_application_create_step3'
    ),
    path(
        'applications/create/<int:application_id>/step4/',
        admin_application_create_step4,
        name='admin_application_create_step4'
    ),
    path(
        'applications/create/<int:application_id>/complete/',
        admin_application_complete,
        name='admin_application_complete'
    ),
    path(
        'applications/<int:application_id>/',
        application_detail,
        name='admin_application_detail'
    ),
    path(
        'applications/<int:application_id>/edit/',
        application_edit_redirect,
        name='admin_application_edit'
    ),
    path(
        'applications/<int:application_id>/edit/basic/',
        admin_application_edit_basic,
        name='admin_application_edit_basic'
    ),
    path(
        'applications/<int:application_id>/edit/management/',
        admin_application_edit_management,
        name='admin_application_edit_management'
    ),
    path(
        'applications/<int:application_id>/edit/transects/',
        admin_application_edit_transects,
        name='admin_application_edit_transects'
    ),
    path(
        'applications/<int:application_id>/submit/',
        admin_application_submit,
        name='admin_application_submit'
    ),
    path(
        'applications/<int:application_id>/delete/',
        application_delete,
        name='admin_application_delete'
    ),
    path(
        'applications/<int:application_id>/link-grower/',
        link_application_to_grower,
        name='admin_application_link_grower'
    ),

    path('transect-codes/', transect_code_list, name='admin_transect_code_list'),
    path('transect-codes/generate/', transect_code_generate, name='admin_transect_code_generate'),
    path(
        'transect-codes/<int:code_id>/deactivate/',
        transect_code_deactivate,
        name='admin_transect_code_deactivate'
    ),
    path(
        'transect-codes/<int:code_id>/reactivate/',
        transect_code_reactivate,
        name='admin_transect_code_reactivate'
    ),

    path('csv-upload/', csv_upload, name='admin_csv_upload'),
    path('csv-imports/', csv_import_list, name='admin_csv_import_list'),
    path('csv-imports/<int:import_id>/', csv_import_detail, name='admin_csv_import_detail'),
    path('csv-imports/<int:import_id>/download/', csv_import_download, name='admin_csv_import_download'),
    path(
        'csv-imports/<int:import_id>/download-error-log/',
        csv_import_download_error_log,
        name='admin_csv_import_download_error_log'
    ),
    path('csv-imports/<int:import_id>/delete/', csv_import_delete, name='admin_csv_import_delete'),

    path('label-management/', label_management, name='label_management'),
    path('label-generations/', label_generation_list, name='label_generation_list'),
    path(
        'label-generations/inner/',
        inner_label_generations_json,
        name='inner_label_generations_json'
    ),
    path('label-generations/<int:generation_id>/', label_generation_detail, name='label_generation_detail'),
    path(
        'label-generations/<int:generation_id>/download/',
        label_generation_download,
        name='label_generation_download'
    ),

    path('submittal-form-generator/', generate_submittal_form, name='submittal_form_generator'),
    path('reports/', report_list, name='admin_report_list'),
    path('reports/<int:report_id>/', report_detail, name='admin_report_detail'),
]
