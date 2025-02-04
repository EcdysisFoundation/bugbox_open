from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import Http404
from rest_framework.viewsets import ReadOnlyModelViewSet

from ..core.constants import COUNTRY_LOOKUP
from ..core.permissions import IS_RESEARCH
from ..core.views import DatatablesModelViewSetMixin
from ..taxonomy import constants as constants_tax
from ..taxonomy.models_query import get_taxon_entries
from . import constants
from .models import Experiment, MultiSpecimenImage, Sample, Site, Specimen
from .serializers import (CollectionDatatablesSerializer,
                          ExperimentsDatatablesSerializer,
                          MultiSpecimenImageDatatablesSerializer,
                          SamplesDatatablesSerializer,
                          SitesDatatablesSerializer,
                          SpecimenDatatablesSerializer,
                          SpecimensAllDatatablesSerializer)
from .views_public import PUBLIC_COLLECTIONS


class ExperimentsDatatablesViewSet(PermissionRequiredMixin, DatatablesModelViewSetMixin, ReadOnlyModelViewSet):

    permission_required = IS_RESEARCH

    serializer_class = ExperimentsDatatablesSerializer
    search_vector = [constants.FIELD_NAME, constants.FIELD_ABBREVIATION]

    def get_queryset(self):
        org_id = int(self.kwargs['org_id'])
        return Experiment.objects.user_access(self.request.user).filter(
            organization_id=org_id).order_by(constants.FIELD_NAME)


class MultiSpecimenDatatablesViewSet(PermissionRequiredMixin,  DatatablesModelViewSetMixin, ReadOnlyModelViewSet):

    permission_required = IS_RESEARCH

    serializer_class = MultiSpecimenImageDatatablesSerializer

    def get_queryset(self):
        return MultiSpecimenImage.objects.user_access(
            self.request.user).filter(sample_id=int(self.kwargs['sample_id']))


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
        return Sample.objects.user_access(
            self.request.user).filter(site_visit__site__experiment_id=experiment_id).order_by(
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
        return Site.objects.user_access(self.request.user).filter(experiment_id=experiment_id).order_by(
            '-' + constants.FIELD_SITE_SITE_NAME
        )


class SpecimenDatatablesViewSet(PermissionRequiredMixin, DatatablesModelViewSetMixin, ReadOnlyModelViewSet):

    permission_required = IS_RESEARCH

    serializer_class = SpecimenDatatablesSerializer
    search_vector = ['classification__name']

    def get_queryset(self):
        sample_id = int(self.kwargs['sample_id'])
        return Specimen.objects.user_access(self.request.user).filter(sample_id=sample_id).order_by('-id')


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
        specimen = Specimen.objects.user_access(self.request.user)
        org_id = int(self.kwargs['org_id'])
        id = int(self.kwargs['id'])
        sample_id = int(self.kwargs['sample_id'])
        if id and not sample_id:
            specimen = specimen.filter(sample__site_visit__site__experiment__id=id)
        elif id and sample_id:
            specimen = specimen.filter(
                sample__site_visit__site__experiment__id=id,
                sample__id=sample_id,
            )
        elif org_id:
            specimen = specimen.filter(
                sample__site_visit__site__experiment__organization_id=org_id,
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
            specimen = specimen.filter(created_by_user_id=int(user))
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


class CollectionDatatablesViewSet(DatatablesModelViewSetMixin, ReadOnlyModelViewSet):

    serializer_class = CollectionDatatablesSerializer
    classification_const = [
        constants_tax.FIELD_MORPHO_GBIF_ORDER,
        constants_tax.FIELD_MORPHO_GBIF_FAMILY,
        constants_tax.FIELD_MORPHO_GBIF_GENUS,
        constants_tax.FIELD_MORPHO_GBIF_SPECIES,
    ]
    search_vector = ['classification__' + v for v in classification_const] + \
                    [constants.FIELD_SPECIMEN_ARCHIVAL_STORED,
                     constants.FIELD_SPECIMEN_ARCHIVAL_IDENTIFIER]

    def get_queryset(self):
        org_id = int(self.kwargs['org_id'])
        if org_id not in PUBLIC_COLLECTIONS.keys():
            raise Http404
        specimen = Specimen.objects.filter(
            sample__site_visit__site__experiment__organization_id=org_id,
            classification_id__isnull=False,
            specimenimage__public_image=True
        )
        archival = self.request.query_params.get('archival')
        if archival:
            specimen = specimen.exclude(
                archival_identifier__isnull=True,
                archival_stored=''
            )
        taxon_filter = self.request.query_params.get('taxon')
        if taxon_filter:
            try:
                tf = int(taxon_filter)
                t_entries = get_taxon_entries(
                    org_id,
                    constants_tax.FIELD_MORPHO_GBIF_FAMILY,
                    public_image=True)
                taxon = [t[1] for t in t_entries if t[0] == tf]
                if taxon:
                    specimen = specimen.filter(classification__gbif_family=taxon[0])
            except Exception:
                raise Http404
        return specimen.exclude(acceptance=0).order_by('-id')
