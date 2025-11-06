"""
Administrator URLs for Grower Portal (is_groweradmin)
"""
from django.urls import path
from ..views.admin import (
    admin_dashboard,
    grower_list, grower_detail,
    farm_list, farm_detail,
    field_list, field_detail,
    application_list, application_detail, application_edit_redirect, application_delete,
    admin_application_edit_basic, admin_application_edit_management,
    admin_application_edit_transects, admin_application_submit,
    transect_code_list, transect_code_generate, transect_code_deactivate, transect_code_reactivate,
    csv_upload, csv_import_list, csv_import_detail,
    report_list, report_detail
)

urlpatterns = [
    path('dashboard/', admin_dashboard, name='admin_dashboard'),
    
    path('growers/', grower_list, name='admin_grower_list'),
    path('growers/<int:grower_id>/', grower_detail, name='admin_grower_detail'),
    
    path('farms/', farm_list, name='admin_farm_list'),
    path('farms/<int:farm_id>/', farm_detail, name='admin_farm_detail'),
    
    path('fields/', field_list, name='admin_field_list'),
    path('fields/<int:field_id>/', field_detail, name='admin_field_detail'),
    
    path('applications/', application_list, name='admin_application_list'),
    path('applications/<int:application_id>/', application_detail, name='admin_application_detail'),
    path('applications/<int:application_id>/edit/', application_edit_redirect, name='admin_application_edit'),
    path('applications/<int:application_id>/edit/basic/', admin_application_edit_basic, name='admin_application_edit_basic'),
    path('applications/<int:application_id>/edit/management/', admin_application_edit_management, name='admin_application_edit_management'),
    path('applications/<int:application_id>/edit/transects/', admin_application_edit_transects, name='admin_application_edit_transects'),
    path('applications/<int:application_id>/submit/', admin_application_submit, name='admin_application_submit'),
    path('applications/<int:application_id>/delete/', application_delete, name='admin_application_delete'),
    
    path('transect-codes/', transect_code_list, name='admin_transect_code_list'),
    path('transect-codes/generate/', transect_code_generate, name='admin_transect_code_generate'),
    path('transect-codes/<int:code_id>/deactivate/', transect_code_deactivate, name='admin_transect_code_deactivate'),
    path('transect-codes/<int:code_id>/reactivate/', transect_code_reactivate, name='admin_transect_code_reactivate'),
    
    path('csv-upload/', csv_upload, name='admin_csv_upload'),
    path('csv-imports/', csv_import_list, name='admin_csv_import_list'),
    path('csv-imports/<int:import_id>/', csv_import_detail, name='admin_csv_import_detail'),
    
    path('reports/', report_list, name='admin_report_list'),
    path('reports/<int:report_id>/', report_detail, name='admin_report_detail'),
]

