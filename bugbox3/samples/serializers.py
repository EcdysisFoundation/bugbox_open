from rest_framework.serializers import ModelSerializer

from .models import Experiment, Sample, Specimen
from . import constants


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
        samples = Sample.objects.filter(experiment_id=v.id)
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

    def to_representation(self, value):
        result = {
            constants.FIELD_UUID: value.uuid,
            constants.FIELD_NAME: value.name,
            constants.FIELD_ABBREVIATION: value.abbreviation,
            'year_span': self.get_years(value)
        }
        result.update(self.get_sample_info(value))
        return result
