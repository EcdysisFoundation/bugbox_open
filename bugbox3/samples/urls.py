from django.urls import include, path
from rest_framework import routers

from .views import ExperimentsView, SpecimensView, ExperimentsDatatablesViewSet

router = routers.DefaultRouter()
router.register(r'experiments-data', ExperimentsDatatablesViewSet)

app_name = "samples"
urlpatterns = [
    path('', include(router.urls)),
    path('experiments/', ExperimentsView.as_view(), name='experiments'),
    path('specimens/', SpecimensView.as_view(), name='specimens'),
]