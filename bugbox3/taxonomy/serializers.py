from rest_framework.serializers import ModelSerializer

from ..libs.ui_helpers import get_datatables_container, get_datatables_row

from .models import Morphospecies

from . import constants


class MorphospeciesDatatablesSerializer(ModelSerializer):

    class Meta:
        model = Morphospecies
        fields = (
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
        return get_datatables_container(get_datatables_row(columns))

    def to_representation(self, value):
        return {
            'data_row': self.get_data_row(value)
        }
