from django.urls import reverse
from rest_framework.serializers import ModelSerializer

from ..libs.ui_helpers import get_datatables_container, get_datatables_row
from . import constants
from .models import Morphospecies


class MorphospeciesDatatablesSerializerMixin(ModelSerializer):
    class Meta:
        model = Morphospecies
        fields = (
            constants.FIELD_MORPHO_ID,
            constants.FIELD_MORPHO_NAME,
            constants.FIELD_MORPHO_GBIF_CANONICAL_NAME,
            constants.FIELD_MORPHO_GBIF_RANK
        )

    def get_data_row(self, value):
        columns = [
            value.name,
            value.gbif_canonical_name,
            value.gbif_rank.upper()
        ]
        return get_datatables_container(get_datatables_row(columns))


class MorphospeciesDatatablesSerializer(MorphospeciesDatatablesSerializerMixin):

    def to_representation(self, value):
        link = reverse('taxonomy:morphospecies-detail', kwargs={'id': value.id})
        data_row = '<a href="{0}" class="text-decoration-none text-dark">{1}</a>'.format(
            link, self.get_data_row(value))
        return {
            'data_row': data_row
        }


class MorphospeciesPickerSerializer(MorphospeciesDatatablesSerializerMixin):

    def get_data_row(self, value):
        columns = [
            value.name,
            value.gbif_canonical_name,
        ]
        return get_datatables_container(get_datatables_row(columns))

    def to_representation(self, value):
        return {
            'data_row': self.get_data_row(value),
            'id': value.id,
            'name': value.name
        }
