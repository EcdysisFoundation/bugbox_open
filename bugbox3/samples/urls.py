from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .exports import experiment_ai_csv, experiment_csv
from .views import (
    ExperimentSamplePlanCreateView,
    ExperimentSamplePlanUpdateView,
    ExperimentsView,
    ExperimentView,
    SampleDeleteView,
    SampleUpdateView,
    SampleView,
    SiteCreateView,
    SiteDeleteView,
    SiteUpdateView,
    SpecimenCreateView,
    SpecimenDeleteView,
    SpecimensView,
    SpecimensWithoutImagesFormView,
    SpecimenUpdateView,
    SpecimenView,
)
from .views_dtables import (
    ExperimentsDatatablesViewSet,
    SamplesDatatablesViewSet,
    SitesDatatablesViewSet,
    SpecimenDatatablesViewSet,
    SpecimensAllDatatablesViewSet,
)

router = DefaultRouter()
router.register(r'experiments-data', ExperimentsDatatablesViewSet,
                basename='experiment-data')
router.register(r'samples-data/(?P<experiment_id>[^/]+)', SamplesDatatablesViewSet,
                basename='sample-data')
router.register(r'sites-data/(?P<experiment_id>[^/]+)', SitesDatatablesViewSet,
                basename='site-data')
router.register(r'specimens-data/(?P<sample_id>[^/]+)', SpecimenDatatablesViewSet,
                basename='specimen-data')
router.register(r'specimens-all-data/(?P<id>[^/]+)/(?P<sample_id>[^/]+)', SpecimensAllDatatablesViewSet,
                basename='specimen-all-data')

app_name = "samples"
urlpatterns = [
     path('', include(router.urls)),
     path('experiments/', ExperimentsView.as_view(), name='experiments'),
     path('experiment/<int:experiment_id>', ExperimentView.as_view(), name='experiment'),
     path('experiment-sample-plan-create/',
          ExperimentSamplePlanCreateView.as_view(), name='experiment-sample-plan-create'),
     path('experiment-sample-plan-update/<int:experiment_id>',
          ExperimentSamplePlanUpdateView.as_view(), name='experiment-sample-plan-update'),
     path('site-create/<int:experiment_id>', SiteCreateView.as_view(), name='site-create'),
     path('site-delete/<int:id>/<int:experiment_id>', SiteDeleteView.as_view(), name='site-delete'),
     path('site-update/<int:site_id>', SiteUpdateView.as_view(), name='site-update'),
     path('sample/<int:sample_id>', SampleView.as_view(), name='sample'),
     path('sample-update/<int:sample_id>', SampleUpdateView.as_view(), name='sample-update'),
     path('sample-delete/<int:id>/<int:experiment_id>', SampleDeleteView.as_view(), name='sample-delete'),
     path('specimen/<int:id>', SpecimenView.as_view(), name='specimen'),
     path('specimen-create/<int:sample_id>', SpecimenCreateView.as_view(), name='specimen-create'),
     path('specimen-update/<int:id>', SpecimenUpdateView.as_view(), name='specimen-update'),
     path('specimen-delete/<int:id>/<int:sample_id>', SpecimenDeleteView.as_view(), name='specimen-delete'),
     path('specimens-experiment-sample/<int:id>/<int:sample_id>',
          SpecimensView.as_view(),
          name='specimens-experiment-sample'),
     path('specimens-wo-img/<int:id>', SpecimensWithoutImagesFormView.as_view(), name='specimens-wo-img'),
     path('experiment-ai-csv/<int:id>', experiment_ai_csv, name='experiment-ai-csv'),
     path('experiment-csv/<int:id>', experiment_csv, name='experiment-csv')
]
