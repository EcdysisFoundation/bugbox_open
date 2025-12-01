from django.http import Http404
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import AllowAny

from ..core.views import DatatablesModelViewSetMixin
from ..samples.models import Experiment, Site, Sample, Specimen
from ..samples.serializers import (
    ExperimentsDatatablesSerializer,
    SitesDatatablesSerializer,
    SpecimenDatatablesSerializer,
)
from ..libs.ui_helpers import (get_classifcation, get_img_src,
                               get_probability_or_user, classify_specimen_button,
                               get_datatables_container, get_datatables_row)
from ..samples import constants
from ..samples.views_demo import get_demo_organization
from ..core.models import LookupChoices
from ..samples.utils import resolve_entered_by
from django.urls import reverse


class DemoExperimentsDatatablesSerializer(ExperimentsDatatablesSerializer):
    
    def get_experiment_link(self, v):
        url = reverse('samples:demo-experiment', kwargs={'experiment_id': v.id})
        return '<a href="{0}" class="link-secondary">{1}</a>'.format(url, v.name)


class DemoExperimentsDatatablesViewSet(DatatablesModelViewSetMixin, ReadOnlyModelViewSet):
    
    permission_classes = [AllowAny]
    serializer_class = DemoExperimentsDatatablesSerializer
    search_vector = [constants.FIELD_NAME, constants.FIELD_ABBREVIATION]

    def get_queryset(self):
        demo_org = get_demo_organization()
        if not demo_org:
            return Experiment.objects.none()
        return Experiment.objects.filter(organization=demo_org).order_by(constants.FIELD_NAME)


class DemoSitesDatatablesSerializer(SitesDatatablesSerializer):
    
    def get_data_row(self, value):
        site_url = reverse('samples:demo-site', kwargs={'site_id': value.id})
        columns = [
            '<a href="{0}" class="link-dark">{1}</a>'.format(
                site_url, value.site_name),
            value.state_region,
            value.county_region,
            value.habitat_type,
            value.treatment
        ]
        return get_datatables_container(get_datatables_row(columns))
    
    def get_sample_data(self, value):
        demo_org = get_demo_organization()
        samples = Sample.objects.filter(
            site_visit__site_id=value.id,
            site_visit__site__experiment__organization=demo_org
        ).order_by(
                'site_visit__' + constants.FIELD_SITE_VISIT_DATE,
                constants.FIELD_SAMPLE_TYPE,
                constants.FIELD_SAMPLE_NAME_NO)
        sample_plans = self.get_sample_plans(value.experiment_id)
        rows = get_datatables_row([
            'Date*',
            'Sample Type',
            'Sample Name',
            'Specimens',
            'Completed',
            'Reviewed',
            'Entered by'
        ])
        for s in samples:
            completed_checkbox = '<i class="bi bi-check-circle-fill text-success"></i>' \
                if s.completed else '<i class="bi bi-x-circle-fill text-danger"></i>'
            if s.sample_type in LookupChoices.objects.get_field_dict_w_blank(
                    value.experiment.organization_id, constants.FIELD_SAMPLE_TYPE).keys():
                sample_type = LookupChoices.objects.get_field_dict_w_blank(
                    value.experiment.organization_id, constants.FIELD_SAMPLE_TYPE)[s.sample_type]
            else:
                sample_type = s.sample_type
            sample_url = reverse('samples:demo-sample', kwargs={'sample_id': s.id})
            rows += get_datatables_row([
                self.get_orphaned(s, sample_plans) + self.get_note(s) +
                s.site_visit.visit_date.strftime("%d-%b-%Y"),
                sample_type,
                '<a href="{0}" class="link-success">{1} <i class="bi bi-bug-fill"></i></a>'.format(
                    sample_url, s.name_no
                ),
                self.get_observations(s.id),
                completed_checkbox,
                self.get_reviewed(s.id),
                resolve_entered_by(s)
            ])

        return get_datatables_container(rows)
    
    def to_representation(self, value):
        result = {
            'data_row': self.get_data_row(value),
            'detail_row': self.get_sample_data(value)
        }
        return result


class DemoSitesDatatablesViewSet(DatatablesModelViewSetMixin, ReadOnlyModelViewSet):
    
    permission_classes = [AllowAny]
    serializer_class = DemoSitesDatatablesSerializer
    search_vector = [constants.FIELD_SITE_SITE_NAME]

    def get_queryset(self):
        demo_org = get_demo_organization()
        if not demo_org:
            return Site.objects.none()
        
        experiment_id = int(self.kwargs['experiment_id'])
        
        try:
            experiment = Experiment.objects.filter(
                organization=demo_org
            ).get(id=experiment_id)
        except Experiment.DoesNotExist:
            raise Http404
        
        return Site.objects.filter(experiment=experiment).order_by(constants.FIELD_SITE_SITE_NAME)


class DemoSpecimenDatatablesSerializer(SpecimenDatatablesSerializer):
    
    def get_data_row(self, value):
        img_exists = False
        if value.specimenimage_set.first():
            img_exists = True
            specimen_image = value.specimenimage_set.first()
            if specimen_image.image_thumbnail:
                img_thumbnail = get_img_src(specimen_image.image_thumbnail, public=specimen_image.public_image)
            else:
                img_thumbnail = get_img_src(specimen_image.image,
                                            constants.SPECIMEN_IMAGE_THUMBSIZE,
                                            public=specimen_image.public_image)
        else:
            img_thumbnail = get_img_src(img_exists)
        link = reverse('samples:demo-specimen', kwargs={'id': value.id})
        columns = [
            '<a href="{0}">{1}</a>'.format(link, img_thumbnail),
            value.partial_count if value.partial_count else '',
            get_classifcation(value),
            get_probability_or_user(value),
        ]
        return get_datatables_container(get_datatables_row(columns))


class DemoSpecimenDatatablesViewSet(DatatablesModelViewSetMixin, ReadOnlyModelViewSet):
    
    permission_classes = [AllowAny]
    serializer_class = DemoSpecimenDatatablesSerializer
    search_vector = ['classification__name', 'ai_classification__name']

    def get_queryset(self):
        demo_org = get_demo_organization()
        if not demo_org:
            return Specimen.objects.none()
        
        sample_id = int(self.kwargs['sample_id'])
        
        try:
            sample = Sample.objects.filter(
                site_visit__site__experiment__organization=demo_org
            ).get(id=sample_id)
        except Sample.DoesNotExist:
            raise Http404
        
        return Specimen.objects.filter(sample=sample).order_by('-id')
