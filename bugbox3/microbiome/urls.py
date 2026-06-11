from django.urls import path

from .views import SiteMicrobiomeTaxaView

app_name = 'microbiome'
urlpatterns = [
    path('site-microbiome-taxa',
         SiteMicrobiomeTaxaView.as_view(),
         name='site-microbiome-taxa')
]
