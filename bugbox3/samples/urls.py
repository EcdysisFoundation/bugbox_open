from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ExperimentSamplePlanCreateView,
    ExperimentSamplePlanUpdateView,
    ExperimentsDatatablesViewSet,
    ExperimentsView,
    ExperimentView,
    SiteCreateView,
    SpecimensView,
)

router = DefaultRouter()
router.register(r'experiments-data', ExperimentsDatatablesViewSet,
                basename='experiment-data')

app_name = "samples"
urlpatterns = [
    path('', include(router.urls)),
    path('experiments/', ExperimentsView.as_view(), name='experiments'),
    path('experiment/<int:experiment_id>', ExperimentView.as_view(), name='experiment'),
    path('specimens/', SpecimensView.as_view(), name='specimens'),
    path('experiment-sample-plan-create/',
         ExperimentSamplePlanCreateView.as_view(), name='experiment-sample-plan-create'),
    path('experiment-sample-plan-update/<int:experiment_id>',
         ExperimentSamplePlanUpdateView.as_view(), name='experiment-sample-plan-update'),
    path('site-create/<int:experiment_id>', SiteCreateView.as_view(), name='site-create')
]
