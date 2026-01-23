"""
Grower Portal URLs
grower and admin subdirectories for separation of concerns
"""
from django.urls import include, path

app_name = 'grower_portal'

urlpatterns = [
    # Grower URLs - require is_grower group membership
    path('', include('bugbox3.grower_portal.urls.grower')),

    # Admin URLs - require is_groweradmin group membership
    path('admin/', include('bugbox3.grower_portal.urls.admin')),
]
