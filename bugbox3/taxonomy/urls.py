from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    MophospeciesDetailView,
    MophospeciesView,
    MorphospeciesDatatablesViewSet,
    classify_sample,
    classify_specimen,
)

router = DefaultRouter()
router.register(r'morphospecies-data', MorphospeciesDatatablesViewSet,
                basename='morphospecies-data')

app_name = "taxonomy"
urlpatterns = [
    path('', include(router.urls)),
    path('morphospecies/', MophospeciesView.as_view(), name='morphospecies'),
    path('morphospecies-detail/<int:id>', MophospeciesDetailView.as_view(), name='morphospecies-detail'),
    path('classify-specimen/<int:id>/', classify_specimen, name='classify-specimen'),
    path('classify-sample/<int:id>/', classify_sample, name='classify-sample'),
]
