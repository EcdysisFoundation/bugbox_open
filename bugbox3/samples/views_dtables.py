from django.contrib.auth.mixins import PermissionRequiredMixin
from rest_framework.viewsets import ReadOnlyModelViewSet

from ..core.constants import COUNTRY_LOOKUP
from ..core.permissions import IS_RESEARCH
from ..core.views import DatatablesModelViewSetMixin
from . import constants
from .models import Experiment, MultiSpecimenImage, Sample, Site, Specimen
from .models_query import get_user_choices
from .serializers import (ExperimentsDatatablesSerializer,
                          MultiSpecimenImageDatatablesSerializer,
                          SamplesDatatablesSerializer,
                          SitesDatatablesSerializer,
                          SpecimenDatatablesSerializer,
                          SpecimensAllDatatablesSerializer)


class ExperimentsDatatablesViewSet(PermissionRequiredMixin, DatatablesModelViewSetMixin, ReadOnlyModelViewSet):

    permission_required = IS_RESEARCH

    serializer_class = ExperimentsDatatablesSerializer
    queryset = Experiment.objects.all().order_by(constants.FIELD_NAME)
    search_vector = [constants.FIELD_NAME, constants.FIELD_ABBREVIATION]


class MultiSpecimenDatatablesViewSet(PermissionRequiredMixin,  DatatablesModelViewSetMixin, ReadOnlyModelViewSet):

    permission_required = IS_RESEARCH

    serializer_class = MultiSpecimenImageDatatablesSerializer

    def get_queryset(self):
        return MultiSpecimenImage.objects.filter(sample_id=int(self.kwargs['sample_id']))


class SamplesDatatablesViewSet(PermissionRequiredMixin, DatatablesModelViewSetMixin, ReadOnlyModelViewSet):

    permission_required = IS_RESEARCH

    serializer_class = SamplesDatatablesSerializer
    search_vector = [
        constants.FIELD_SAMPLE_TYPE,
        constants.FIELD_SAMPLE_NAME_NO,
        'site_visit__site__' + constants.FIELD_SITE_SITE_NAME
    ]

    def get_queryset(self):
        experiment_id = int(self.kwargs['experiment_id'])
        return Sample.objects.filter(site_visit__site__experiment_id=experiment_id).order_by(
            '-site_visit__site__' + constants.FIELD_SITE_SITE_NAME, constants.FIELD_SAMPLE_NAME_NO
        )


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
        return Site.objects.filter(experiment_id=experiment_id).order_by(
            '-' + constants.FIELD_SITE_SITE_NAME
        )


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
        'archival_identifier',
        'archival_stored'
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
        acceptance = self.request.query_params.get('acceptance')
        if acceptance:
            if acceptance.isnumeric():
                acceptance = int(acceptance)
            if acceptance in constants.ACCEPTANCE_VALID:
                specimen = specimen.filter(acceptance=acceptance)
            elif acceptance == 'Reviewed':
                specimen = specimen.exclude(acceptance=constants.ACCEPTANCE_PENDING)
        archival = self.request.query_params.get('archival')
        if archival:
            specimen = specimen.exclude(
                archival_identifier__isnull=True,
                archival_preservation='',
                archival_stored=''
            )
        user = self.request.query_params.get('user')
        if user:
            users = [v[0] for v in get_user_choices()]
            user = int(user)
            if user in users:
                specimen = specimen.filter(created_by_user_id=user)
        state = self.request.query_params.get('state')
        if state:
            specimen = specimen.filter(sample__site_visit__site__state_region=state)
        country = self.request.query_params.get('country')
        if country:
            specimen = specimen.filter(sample__site_visit__site__country=COUNTRY_LOOKUP[country])
        tag = self.request.query_params.get('tag')
        if tag:
            specimen = specimen.filter(tags__contains=[tag])
        sample_type = self.request.query_params.get('sample_type')
        if sample_type:
            specimen = specimen.filter(sample__sample_type=sample_type)
        recent_year = self.request.query_params.get('recent_year')
        if recent_year:
            specimen = specimen.filter(sample__site_visit__visit_date__year=recent_year)
        classification_filter = self.request.query_params.get('classification_filter')
        classification_radio = self.request.query_params.get('classification_radio')
        ai_classification_radio = self.request.query_params.get('ai_classification_radio')
        if classification_filter:
            if classification_radio:
                if classification_filter.replace(' ', '').isalnum():
                    specimen = specimen.filter(classification__name__icontains=classification_filter)
            elif ai_classification_radio:
                if classification_filter.replace(' ', '').isalnum():
                    specimen = specimen.filter(ai_classification__name__icontains=classification_filter)
        return specimen.order_by('-id')
