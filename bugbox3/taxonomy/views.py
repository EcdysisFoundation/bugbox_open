from django.views.generic import TemplateView
from rest_framework.reverse import reverse as api_reverse
from rest_framework.viewsets import ReadOnlyModelViewSet

from ..core.views import DatatablesModelViewSetMixin
from ..libs.utilities import get_json_context
from ..libs.ui_helpers import (get_datatables_container, get_datatables_row)

from .models import Morphospecies
from .serializers import MorphospeciesDatatablesSerializer

from . import constants


class MorphospeciesDatatablesViewSet(DatatablesModelViewSetMixin, ReadOnlyModelViewSet):
    serializer_class = MorphospeciesDatatablesSerializer
    search_vector = (constants.FIELD_MORPHO_NAME,
            constants.FIELD_MORPHO_GBIF_CANONICAL_NAME)

    def get_queryset(self):
        if self.request.query_params.get('first_filter'):
            gbif_rank = self.request.query_params.get('first_filter')
            if gbif_rank in constants.GBIF_RANK_VALUES:
                return Morphospecies.objects.filter(gbif_rank=gbif_rank).order_by(constants.FIELD_MORPHO_NAME)
        return Morphospecies.objects.all().order_by(constants.FIELD_MORPHO_NAME)

class MophospeciesView(TemplateView):
    template_name = 'taxonomy/morphospecies.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lendata = Morphospecies.objects.all().count()
        datatables_url = api_reverse('taxonomy:morphospecies-data-list',
                                        request=self.request, kwargs=kwargs)
        context.update({
            'json_context': get_json_context({
                'datatables_url': datatables_url,
                'first_picker_choices': constants.GBIF_RANK_CHOICES_WO_BLANK_LIST,
                'first_picker_name': 'rank'
            }),
            'container_row_header': get_datatables_container(
                get_datatables_row([
                    'Name',
                    'Canonical Name',
                    'Rank'
                ])),
        })
        return context
