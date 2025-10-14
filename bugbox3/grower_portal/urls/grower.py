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
    
]


