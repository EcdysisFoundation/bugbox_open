"""
Grower URLs for Grower Portal
All URLs require is_grower group membership
"""
from django.urls import path
from ..views.grower.views import profile_complete, dashboard, profile_edit

# Note: app_name is set in parent urls/__init__.py
urlpatterns = [
    # Profile Management
    path('profile/complete/', profile_complete, name='profile_complete'),
    path('profile/edit/', profile_edit, name='profile_edit'),
    
    # Dashboard
    path('dashboard/', dashboard, name='dashboard'),
    
    # Future URLs (placeholder comments):
    # Application Management
    # path('applications/create/', application_create, name='application_create'),
    # path('applications/<int:application_id>/step-1/', application_step1, name='application_step1'),
    # path('applications/<int:application_id>/step-2/', application_step2, name='application_step2'),
    # path('applications/<int:application_id>/step-3/', application_step3, name='application_step3'),
    # path('applications/<int:application_id>/step-4/', application_step4, name='application_step4'),
    # path('applications/<int:application_id>/step-5/', application_step5, name='application_step5'),
    # path('applications/<int:application_id>/submit/', application_submit, name='application_submit'),
    
    # Farm & Field Management
    # path('farms/', farm_list, name='farm_list'),
    # path('farms/create/', farm_create, name='farm_create'),
    # path('farms/<int:farm_id>/edit/', farm_edit, name='farm_edit'),
    # path('farms/<int:farm_id>/fields/', field_list, name='field_list'),
    # path('farms/<int:farm_id>/fields/create/', field_create, name='field_create'),
    # path('farms/<int:farm_id>/fields/<int:field_id>/edit/', field_edit, name='field_edit'),
    
    # Reports
    # path('reports/', my_reports, name='my_reports'),
]


