from django.urls import reverse
from rest_framework.serializers import ModelSerializer

from bugbox3.libs.ui_helpers import get_datatables_container, get_datatables_row, get_img_src

from . import constants
from .models import Experiment, Sample, Site, Specimen


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
        result = dict(
            total_samples='0',
            photo_sampling='',
            not_reviewed=''
        )
        samples = Sample.objects.filter(site_visit__site__experiment_id=v.id)
        if not samples:
            return result
        sample_ids = [s.id for s in samples]
        if sample_ids:
            result['total_samples'] = str(len(sample_ids))
            result['photo_sampling'] = str(samples.filter(completed=False).count())
            specimens = Specimen.objects.filter(sample_id__in=sample_ids)
            if specimens:
                result['not_reviewed'] = specimens.filter(acceptance=constants.ACCEPTANCE_PENDING).count()
        return result

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
            sample_info['not_reviewed'],

        ]
        return get_datatables_container(get_datatables_row(columns))

    def to_representation(self, value):
        return {
            'data_row': self.get_data_row(value)
        }


class SamplesDatatablesSerializer(ModelSerializer):

    class Meta:
        model = Sample
        fields = [constants.FIELD_SAMPLE_TYPE]

    def get_data_row(self, value):
        columns = [
            value.sample_type,
            value.site_visit.visit_date,
            value.site_visit.site.site_name
        ]
        return get_datatables_container(get_datatables_row(columns))

    def to_representation(self, value):
        result = {
            'data_row': self.get_data_row(value),
        }
        return result


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

    def get_sample_data(self, value):
        samples = Sample.objects.filter(
            site_visit__site_id=value.id)
        rows = get_datatables_row([
            'Date',
            'Sample Type',
            'Sample Name',
            'Observations',
            'Reviewed',
            'Entered by'
        ])
        for s in samples:
            if s.sample_type in constants.SAMPLE_TYPE_CHOICES_DICT.keys():
                sample_type = constants.SAMPLE_TYPE_CHOICES_DICT[s.sample_type]
            else:
                sample_type = s.sample_type
            sample_url = reverse('samples:sample', kwargs={'sample_id': s.id})
            rows += get_datatables_row([
                s.site_visit.visit_date,
                '<a href="{0}" class="link-success">{1} <i class="bi bi-bug-fill"></i></a>'.format(
                    sample_url, sample_type),
                s.name_no,
                self.get_observations(s.id),
                self.get_reviewed(s.id),
                'P. Laceholder'  # add field to model and populate at create
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
            constants.FIELD_SPECIMEN_ARCHIVAL_IDENTIFIER,
            'specimen_image'
        ]

    def get_id_checkbox(self, value):
        return '<input type="checkbox" name="specimen_id" value="{0}" />'.format(value.id)

    def get_data_row(self, value):
        if value.specimenimage_set.first():
            specimen_image = value.specimenimage_set.first()
            if specimen_image.image_thumbnail:
                img_thumbnail = get_img_src(specimen_image.image_thumbnail)
            else:
                img_thumbnail = get_img_src(specimen_image.image)
        else:
            img_thumbnail = get_img_src(None)
        columns = [
            img_thumbnail,
            value.partial_count,
            'ai_classification',  # value.ai_classification.name,
            'Pending',  # replace with value.confidence and value.ai_version.version
            # self.get_id_checkbox(value),
        ]
        return get_datatables_container(get_datatables_row(columns))

    def to_representation(self, value):
        return {
            'data_row': self.get_data_row(value),
            # 'classification': value.ai_classification.name,
        }
