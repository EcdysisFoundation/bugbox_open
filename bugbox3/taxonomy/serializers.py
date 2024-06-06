from django.urls import reverse
from rest_framework.serializers import ModelSerializer

from ..libs.ui_helpers import get_datatables_container, get_datatables_row

from .models import Morphospecies

from . import constants


class MorphospeciesDatatablesSerializer(ModelSerializer):

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
            value.gbif_rank
        ]
        #get_datatables_row(columns, col_styles=['link-underline-opacity-0'])
        return get_datatables_container(get_datatables_row(columns))

    def to_representation(self, value):
        link = reverse('taxonomy:morphospecies-detail', kwargs={'id': value.id})
        data_row = '<a href="{0}" class="text-decoration-none text-dark">{1}</a>'.format(link, self.get_data_row(value))
        return {
            'data_row': data_row
        }
