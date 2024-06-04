from django.views.generic import TemplateView
from rest_framework.reverse import reverse as api_reverse
from rest_framework.viewsets import ReadOnlyModelViewSet

from ..core.views import DatatablesModelViewSetMixin
from ..libs.utilities import get_json_context
from ..libs.ui_helpers import (get_datatables_container, get_datatables_row)

from .models import Morphospecies
from .serializers import MorphospeciesDatatablesSerializer


class MorphospeciesDatatablesViewSet(DatatablesModelViewSetMixin, ReadOnlyModelViewSet):
    serializer_class = MorphospeciesDatatablesSerializer
    queryset = Morphospecies.objects.all().order_by('name')
    search_vector = ['name']

class MophospeciesView(TemplateView):
    template_name = 'taxonomy/morphospecies.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lendata = Morphospecies.objects.all().count()
        datatables_url = api_reverse('taxonomy:morphospecies-data-list',
                                        request=self.request, kwargs=kwargs)
        context.update({
            'json_context': get_json_context({'datatables_url': datatables_url}),
            'lendata': lendata,
            'container_row_header': get_datatables_container(
                get_datatables_row([
                    'Name',
                ])),
        })
        return context
