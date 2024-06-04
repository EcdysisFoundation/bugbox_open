from rest_framework.serializers import ModelSerializer

from ..libs.ui_helpers import get_datatables_container, get_datatables_row

from .models import Morphospecies


class MorphospeciesDatatablesSerializer(ModelSerializer):

    class Meta:
        model = Morphospecies
        fields = ['name']

    def get_data_row(self, value):
        columns = [
            value.name,
        ]
        return get_datatables_container(get_datatables_row(columns))

    def to_representation(self, value):
        return {
            'data_row': self.get_data_row(value)
        }
