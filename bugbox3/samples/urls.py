from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (ExperimentsView, SpecimensView, ExperimentsDatatablesViewSet, 
                    ExperimentSamplePlanCreateView)

router = DefaultRouter()
router.register(r'experiments-data', ExperimentsDatatablesViewSet,
                basename='experiment-data')

app_name = "samples"
urlpatterns = [
    path('', include(router.urls)),
    path('experiments/', ExperimentsView.as_view(), name='experiments'),
    path('specimens/', SpecimensView.as_view(), name='specimens'),
    path('experiment-sample-plan-create/', ExperimentSamplePlanCreateView.as_view(), name='experiment-sample-plan-create')
]
