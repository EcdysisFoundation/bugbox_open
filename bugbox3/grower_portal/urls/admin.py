"""
Administrator URLs for Grower Portal
All URLs require is_groweradmin group membership
"""
from django.urls import path

# Note: app_name is set in parent urls/__init__.py
urlpatterns = [
    # Future admin URLs (placeholder comments):
    
    # Admin Dashboard
    # path('dashboard/', admin_dashboard, name='admin_dashboard'),
    
    # Grower Management
    # path('growers/', grower_list, name='admin_grower_list'),
    # path('growers/<int:grower_id>/', grower_detail, name='admin_grower_detail'),
    
    # Application Management
    # path('applications/', application_list, name='admin_application_list'),
    # path('applications/<int:application_id>/', application_detail, name='admin_application_detail'),
    
    # Transect Code Management
    # path('transect-codes/', transect_code_list, name='admin_transect_code_list'),
    # path('transect-codes/generate/', generate_transect_codes, name='admin_generate_transect_codes'),
    
    # CSV Upload
    # path('csv-upload/', csv_upload, name='admin_csv_upload'),
    # path('csv-logs/', csv_import_logs, name='admin_csv_logs'),
    
    # Reports
    # path('reports/', report_list, name='admin_report_list'),
]

