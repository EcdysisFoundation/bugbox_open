from django.core.files.storage import default_storage
from django.urls import reverse
from rest_framework.serializers import ModelSerializer

from ..core.models import LookupChoices
from ..libs.ui_helpers import (classify_specimen_button, get_ai_classification,
                               get_canonical_name, get_classifcation,
                               get_datatables_container, get_datatables_row,
                               get_img_captioned, get_img_src,
                               get_probability_or_user, get_specimen_context,
                               get_specimen_location)
from ..libs.utilities import get_media_url
from . import constants
from .models import (Experiment, MultiSpecimenImage, Sample, SamplePlan, Site,
                     Specimen)
from bugbox3.samples.utils import resolve_entered_by


class ExperimentsDatatablesSerializer(ModelSerializer):

    class Meta:
        model = Experiment
        fields = [constants.FIELD_UUID, constants.FIELD_NAME,
                  constants.FIELD_ABBREVIATION, constants.FIELD_FROM_YEAR,
                  constants.FIELD_TO_YEAR]

    def get_years(self, v):
        if v.from_year == v.to_year:
            return str(v.from_year)
        else:
            return str(v.from_year) + ' - ' + str(v.to_year)

    def get_sample_info(self, v):
        return {
            'total_samples': Sample.objects.filter(
                site_visit__site__experiment_id=v.id).count(),
            'photo_sampling': Sample.objects.filter(
                site_visit__site__experiment_id=v.id, completed=False).count(),
            'not_reviewed': Specimen.objects.filter(
                sample__site_visit__site__experiment_id=v.id,
                acceptance=constants.ACCEPTANCE_PENDING).distinct('sample_id').count()
        }

    def get_experiment_link(self, v):
        url = reverse('samples:experiment', kwargs={'experiment_id': v.id})
        return '<a href="{0}" class="link-secondary">{1}</a>'.format(url, v.name)

    def get_data_row(self, value):
        sample_info = self.get_sample_info(value)
        columns = [
            self.get_experiment_link(value),
            value.abbreviation,
            self.get_years(value),
            sample_info['total_samples'],
            sample_info['photo_sampling'],
            sample_info['not_reviewed']
        ]
        return get_datatables_container(get_datatables_row(columns))

    def to_representation(self, value):
        return {
            'data_row': self.get_data_row(value)
        }


class MultiSpecimenImageDatatablesSerializer(ModelSerializer):

    class Meta:
        model = MultiSpecimenImage
        fields = ['id', 'image_4_by_3_thumbnail', 'cropped_to_specimen']

    def get_data_row(self, value):
        columns = [
            get_img_src(value.image_thumbnail),
            value.cropped_to_specimen
        ]
        return get_datatables_container(get_datatables_row(columns))

    def to_representation(self, value):
        return {
            'id': value.id,
            'data_row': self.get_data_row(value),
        }


class SamplesDatatablesSerializer(ModelSerializer):

    class Meta:
        model = Sample
        fields = [
            constants.FIELD_SAMPLE_TYPE,
            constants.FIELD_SAMPLE_NAME_NO
        ]

    def get_data_row(self, value):
        columns = [
            value.site_visit.site.site_name,
            value.site_visit.visit_date.strftime("%d-%b-%Y"),
            value.sample_type,
            value.name_no
        ]
        return get_datatables_container(get_datatables_row(columns))

    def to_representation(self, value):
        return {
            'sample_id': value.id,
            'data_row': self.get_data_row(value),
        }


class SitesDatatablesSerializer(ModelSerializer):

    class Meta:
        model = Site
        fields = [
            constants.FIELD_SITE_SITE_NAME,
            constants.FIELD_SITE_STATE_REGION,
            constants.FIELD_SITE_COUNTY_REGION,
            constants.FIELD_SITE_HABITAT_TYPE,
            constants.FIELD_SITE_TREATMENT,
        ]

    def get_observations(self, id):
        return Specimen.objects.filter(sample_id=id).count()

    def get_reviewed(self, id):
        return Specimen.objects.filter(sample_id=id, acceptance__gt=0).count()

    def get_orphaned(self, s, sample_plans):
        warning = '<i class="bi bi-exclamation-triangle text-warning"></i> '
        if not sample_plans['sample_types']:
            return ''
        if s.sample_type not in sample_plans['sample_types']:
            return warning
        if s.name_no not in sample_plans['sample_names']:
            return warning
        return ''

    def get_sample_plans(self, experiment_id):
        sample_plans = SamplePlan.objects.filter(experiment_id=experiment_id)
        sample_types = []
        sample_names = []
        for plan in sample_plans:
            n = plan.no_per_date
            while n:
                name = str(plan.name_no_per_type) + str(n)
                sample_types.append(plan.sample_type)
                sample_names.append(name)
                n = n - 1
        return {
            'sample_types': sample_types,
            'sample_names': sample_names
        }

    def get_note(self, s):
        if s.notes:
            return '<i class="bi bi-info-square text-info"></i> '
        return ''

    def get_sample_data(self, value):
        samples = Sample.objects.filter(
            site_visit__site_id=value.id).order_by(
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
            sample_url = reverse('samples:sample', kwargs={'sample_id': s.id})
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

    def get_data_row(self, value):
        site_url = reverse('samples:site-update', kwargs={'site_id': value.id})
        columns = [
            '<a href="{0}" class="link-dark">{1} &nbsp;&nbsp;<i class="bi bi-pencil"></i></a>'.format(
                site_url, value.site_name),
            value.state_region,
            value.county_region,
            value.habitat_type,
            value.treatment
        ]
        return get_datatables_container(get_datatables_row(columns))

    def to_representation(self, value):
        result = {
            'data_row': self.get_data_row(value),
            'detail_row': self.get_sample_data(value)
        }
        return result


class SpecimenDatatablesSerializer(ModelSerializer):

    class Meta:
        model = Specimen
        fields = [
            constants.FIELD_SPECIMEN_PARTIAL_COUNT,
            constants.FIELD_SPECIMEN_ACCEPTANCE,
            constants.FIELD_SPECIMEN_CONFIDENCE,
            constants.FIELD_SPECIMEN_ARCHIVAL_IDENTIFIER
        ]

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
        link = reverse('samples:specimen', kwargs={'id': value.id})
        columns = [
            '<a href="{0}">{1}</a>'.format(link, img_thumbnail),
            value.partial_count if value.partial_count else '',
            get_classifcation(value),
            get_probability_or_user(value),
            classify_specimen_button(value, img_exists)
        ]
        return get_datatables_container(get_datatables_row(columns))

    def to_representation(self, value):
        return {
            'specimen_id': value.id,
            'data_row': self.get_data_row(value),
        }


class SpecimensAllDatatablesSerializer(ModelSerializer):

    class Meta:
        model = Specimen
        fields = [
            constants.FIELD_SPECIMEN_PARTIAL_COUNT,
            constants.FIELD_SPECIMEN_ACCEPTANCE,
            constants.FIELD_SPECIMEN_CONFIDENCE,
            constants.FIELD_SPECIMEN_ARCHIVAL_IDENTIFIER
        ]

    def to_representation(self, value):
        img_thumbnail_large = None
        specimen_image = value.specimenimage_set.first()
        if specimen_image:
            img_thumbnail = get_img_src(specimen_image.image_thumbnail, public=specimen_image.public_image)
            if specimen_image.image_thumbnail_large:
                # dont use get_img_src() here due to modal .js reasons
                if default_storage.exists(specimen_image.image_thumbnail_large.name):
                    img_thumbnail_large = {
                        'url': get_media_url(
                            specimen_image.image_thumbnail_large, public=specimen_image.public_image),
                        'width': getattr(specimen_image.image_thumbnail_large, 'width', ''),
                        'height': getattr(specimen_image.image_thumbnail_large, 'height', '')
                    }
                else:
                    img_thumbnail_large = {
                        'url': '',
                        'width': '',
                        'height': ''
                    }
        else:
            img_thumbnail = get_img_src(False)
        return {
            'archival_identifier': value.archival_identifier,
            'archival_stored': value.archival_stored,
            'img_thumbnail': img_thumbnail,
            'img_thumbnail_large': img_thumbnail_large,
            'id': value.id,
            'has_image': True if specimen_image else False,
            'acceptance': value.acceptance,
            'ai_classification_name': value.ai_classification.name if value.ai_classification else '',
            'ai_classification': get_ai_classification(value),
            'classification_name': value.classification.name if value.classification else '',
            'gbif_canonical_name': get_canonical_name(value.classification) if value.classification else '',
            'classification_id': value.classification.id if value.classification else '',
            'view_link': reverse('samples:specimen', kwargs={'id': value.id}),
            'edit_link': reverse('samples:specimen-update', kwargs={'id': value.id}),
            'specimen_context': get_specimen_context(value)
        }


class CollectionDatatablesSerializer(ModelSerializer):

    class Meta:
        model = Specimen
        fields = [
            constants.FIELD_SPECIMEN_ARCHIVAL_IDENTIFIER
        ]

    def to_representation(self, value):
        img_thumbnail_large = None
        specimen_image = value.specimenimage_set.first()
        if specimen_image:
            image = get_img_captioned(
                    specimen_image.image_thumbnail_medium,
                    value.classification.gbif_canonical_name,
                    public=specimen_image.public_image)
            if specimen_image.image_thumbnail_large:
                # dont use get_img_src() here due to modal .js reasons
                if default_storage.exists(specimen_image.image_thumbnail_large.name):
                    img_thumbnail_large = {
                        'url': get_media_url(
                            specimen_image.image_thumbnail_large, public=specimen_image.public_image),
                        'width': getattr(specimen_image.image_thumbnail_large, 'width', ''),
                        'height': getattr(specimen_image.image_thumbnail_large, 'height', '')
                    }
                else:
                    img_thumbnail_large = {
                        'url': '',
                        'width': '',
                        'height': ''
                    }
        else:
            image = get_img_src(False)
        archival = value.archival_identifier
        if archival and value.archival_stored:
            archival += ' | ' + value.archival_stored
        else:
            archival = value.archival_stored
        return {
            'image': image,
            'img_thumbnail_large': img_thumbnail_large,
            'taxonomy': {
                'gbif_order': value.classification.gbif_order,
                'gbif_family': value.classification.gbif_family,
                'species': value.classification.gbif_species
                if value.classification.gbif_species
                else value.classification.gbif_genus + ' spp.'
                if value.classification.gbif_genus else '',
            },
            'details': {
                'visit_date': value.sample.site_visit.visit_date,
                'location': get_specimen_location(value),
                'archival': archival}
        }
