from django.contrib.auth.mixins import PermissionRequiredMixin
from rest_framework.viewsets import ReadOnlyModelViewSet

from ..core.views import DatatablesModelViewSetMixin

from .serializers import (
    ExperimentsDatatablesSerializer,
    SamplesDatatablesSerializer,
    SitesDatatablesSerializer,
    SpecimenDatatablesSerializer,
    SpecimensAllDatatablesSerializer,
)

from ..core.permissions import IS_RESEARCH
from .models import Experiment, Sample, Site, Specimen
from . import constants

class ExperimentsDatatablesViewSet(PermissionRequiredMixin, DatatablesModelViewSetMixin, ReadOnlyModelViewSet):

    permission_required = IS_RESEARCH

    serializer_class = ExperimentsDatatablesSerializer
    queryset = Experiment.objects.all().order_by(constants.FIELD_NAME)
    search_vector = [constants.FIELD_NAME, constants.FIELD_ABBREVIATION]


class SamplesDatatablesViewSet(PermissionRequiredMixin, DatatablesModelViewSetMixin, ReadOnlyModelViewSet):

    permission_required = IS_RESEARCH

    serializer_class = SamplesDatatablesSerializer
    search_vector = [constants.FIELD_SAMPLE_TYPE]

    def get_queryset(self):
        experiment_id = int(self.kwargs['experiment_id'])
        return Sample.objects.filter(site_visit__site__experiment_id=experiment_id)


class SitesDatatablesViewSet(PermissionRequiredMixin, DatatablesModelViewSetMixin, ReadOnlyModelViewSet):

    permission_required = IS_RESEARCH

    serializer_class = SitesDatatablesSerializer
    search_vector = [
            constants.FIELD_SITE_SITE_NAME,
            constants.FIELD_SITE_STATE_REGION,
            constants.FIELD_SITE_HABITAT_TYPE,
            constants.FIELD_SITE_TREATMENT
        ]

    def get_queryset(self):
        experiment_id = int(self.kwargs['experiment_id'])
        return Site.objects.filter(experiment_id=experiment_id)


class SpecimenDatatablesViewSet(PermissionRequiredMixin, DatatablesModelViewSetMixin, ReadOnlyModelViewSet):

    permission_required = IS_RESEARCH

    serializer_class = SpecimenDatatablesSerializer
    search_vector = ['classification__name']

    def get_queryset(self):
        sample_id = int(self.kwargs['sample_id'])
        return Specimen.objects.filter(sample_id=sample_id).order_by('-id')


class SpecimensAllDatatablesViewSet(PermissionRequiredMixin, DatatablesModelViewSetMixin, ReadOnlyModelViewSet):

    permission_required = IS_RESEARCH

    serializer_class = SpecimensAllDatatablesSerializer
    search_vector = [
        'classification__name',
        'ai_classification__name',
    ]

    def get_queryset(self):
        specimen = Specimen.objects.filter(
            sample__site_visit__site__experiment__isnull=False
        )
        id = int(self.kwargs['id'])
        sample_id = int(self.kwargs['sample_id'])
        if id and not sample_id:
            specimen = specimen.filter(sample__site_visit__site__experiment__id=id)
        elif id and sample_id:
            specimen = specimen.filter(
                sample__site_visit__site__experiment__id=id,
                sample__id=sample_id,
            )
        if self.request.query_params.get('acceptance_filter'):
            acceptance = self.request.query_params.get('acceptance_filter')
            specimen = specimen.filter(acceptance=acceptance)
        if self.request.query_params.get('class_filter'):
            if self.request.query_params.get('class_filter'):
                specimen = specimen.filter(classification_id__isnull=True)
        return specimen.order_by('-id')
