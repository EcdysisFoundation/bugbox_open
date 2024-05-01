from django.urls import reverse
from rest_framework.serializers import ModelSerializer

from bugbox3.libs.ui_helpers import get_datatables_container, get_datatables_row

from . import constants
from .models import Experiment, Sample, Specimen, Site


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
                result['not_reviewed'] = specimens.filter(acceptance=constants.ACCEPTANCE_PENDING)
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
            site_visit__site__experiment_id=value.experiment_id)
        rows = get_datatables_row([
            'Date',
            'Sample Type',
            'Sample Name',
            'Observations',
            'Reviewed',
            'Entered by'
        ])
        for s in samples:
            rows += get_datatables_row([
                s.site_visit.visit_date,
                s.sample_type,
                s.name_no,
                self.get_observations(s.id),
                self.get_reviewed(s.id),
                'P. Laceholder' # add field to model and populate at create
            ])
        return get_datatables_container(rows)

    
    def get_data_row(self, value):
        columns = [
            value.site_name,
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