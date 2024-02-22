from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (ExperimentsView, SpecimensView, ExperimentsDatatablesViewSet, 
                    ExperimentCreateView, ExperimentCreateView2, ExperimentSamplePlanCreateView,
                    experiment_create_view)

router = DefaultRouter()
router.register(r'experiments-data', ExperimentsDatatablesViewSet,
                basename='experiment-data')

app_name = "samples"
urlpatterns = [
    path('', include(router.urls)),
    path('experiments/', ExperimentsView.as_view(), name='experiments'),
    path('specimens/', SpecimensView.as_view(), name='specimens'),
    path('experiment-create/', ExperimentCreateView.as_view(), name='experiment-create'),
    path('experiment-sample-plan-create', experiment_create_view, name='experiment-sample-plan-create'),
    path('experiment-create-plan', ExperimentCreateView2.as_view(), name='experiment-create-plan'),
    path('experiment-create-plan3', ExperimentSamplePlanCreateView.as_view(), name='experiment-create-plan3')
]
