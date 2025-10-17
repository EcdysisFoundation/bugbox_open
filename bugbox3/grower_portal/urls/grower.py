"""
Grower URLs for Grower Portal
All URLs require is_grower group membership
"""
from django.urls import path
from ..views.grower.views import (
    profile_complete, dashboard, profile_edit,
    application_create, application_step1, application_step2,
    application_step3, application_step4, application_step5,
    application_view, application_edit, application_delete
)

urlpatterns = [
    path('profile/complete/', profile_complete, name='profile_complete'),
    path('profile/edit/', profile_edit, name='profile_edit'),
    path('dashboard/', dashboard, name='dashboard'),
    path('applications/create/', application_create, name='application_create'),
    path('applications/<int:application_id>/', application_view, name='application_view'),
    path('applications/<int:application_id>/edit/', application_edit, name='application_edit'),
    path('applications/<int:application_id>/delete/', application_delete, name='application_delete'),
    path('applications/<int:application_id>/step1/', application_step1, name='application_step1'),
    path('applications/<int:application_id>/step2/', application_step2, name='application_step2'),
    path('applications/<int:application_id>/step3/', application_step3, name='application_step3'),
    path('applications/<int:application_id>/step4/', application_step4, name='application_step4'),
    path('applications/<int:application_id>/step5/', application_step5, name='application_step5'),
]


