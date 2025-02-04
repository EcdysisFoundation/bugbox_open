from django.http import Http404
from django.views.generic import TemplateView
from rest_framework.reverse import reverse as api_reverse

from ..libs.utilities import get_json_context
from ..taxonomy import constants as constants_tax
from ..taxonomy.models_query import get_taxon_entries

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
            'org_name': PUBLIC_COLLECTIONS[self.kwargs['org_id']]['org_name'],
            'family_choices': get_taxon_entries(
                    kwargs['org_id'],
                    constants_tax.FIELD_MORPHO_GBIF_FAMILY,
                    public_image=True),
            'json_context': get_json_context({
                'collection': PUBLIC_COLLECTIONS[self.kwargs['org_id']]['collection'],
                'datatables_url': api_reverse('samples:collection-data-list',
                                              request=self.request, kwargs=kwargs),
            })
        })
        return context
