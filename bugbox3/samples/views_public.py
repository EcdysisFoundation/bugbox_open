from django.http import Http404
from django.views.generic import TemplateView
from rest_framework.reverse import reverse as api_reverse

from ..libs.ui_helpers import get_datatables_container, get_datatables_row
from ..libs.utilities import get_json_context

# These can become entries in the Organization model when more orgs have public data.
ECDYSIS_COLLECTION = 'The Mark F. Longfellow Ecological Reference Collection'
PUBLIC_COLLECTIONS = {1: {
    'org_name': 'Ecdysis Foundation',
    'collection': ECDYSIS_COLLECTION}}


class CollectionView(TemplateView):

    template_name = 'pages/collections.html'

    def get_context_data(self, **kwargs):
        context = super(CollectionView, self).get_context_data(**kwargs)
        if kwargs['org_id'] not in PUBLIC_COLLECTIONS.keys():
            raise Http404
        context.update({
            'collection': PUBLIC_COLLECTIONS[self.kwargs['org_id']]['collection'],
            'org_name': PUBLIC_COLLECTIONS[self.kwargs['org_id']]['org_name'],
            'container_row_header': get_datatables_container(
                get_datatables_row([
                    'Image'])),
            'json_context': get_json_context({
                'datatables_url': api_reverse('samples:collection-data-list',
                                              request=self.request, kwargs=kwargs)
            })
        })
        return context
