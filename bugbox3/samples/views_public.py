from django.http import Http404
from django.views.generic import TemplateView
from rest_framework.reverse import reverse as api_reverse

from ..core.models import Exports
from ..libs.ui_helpers import get_img_captioned, get_specimen_location
from ..libs.utilities import get_json_context, get_media_url
from ..samples.exports import PUBLIC_IMAGES_EXPORT_TITLE
from ..samples.models import SpecimenImage
from ..taxonomy import constants as constants_tax
from ..taxonomy.models_query import get_taxon_entries

# These can become entries in the Organization model when more orgs have public data.
ECDYSIS_COLLECTION = 'The Mark F. Longfellow Ecological Reference Collection'
PUBLIC_COLLECTIONS = {1: {
    'org_name': 'Ecdysis Foundation',
    'collection': ECDYSIS_COLLECTION,
    'example_img_id': 36314,
    'homepage': 'https://www.ecdysis.bio/'}}


class CollectionView(TemplateView):

    template_name = 'pages/collections.html'

    def get_context_data(self, **kwargs):
        context = super(CollectionView, self).get_context_data(**kwargs)
        if kwargs['org_id'] not in PUBLIC_COLLECTIONS.keys():
            raise Http404
        context.update({
            'org_name': PUBLIC_COLLECTIONS[self.kwargs['org_id']]['org_name'],
            'org_id': self.kwargs['org_id'],
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


class CollectionDownloadView(TemplateView):

    template_name = 'pages/collection_download.html'

    def get_context_data(self, **kwargs):
        context = super(CollectionDownloadView, self).get_context_data(**kwargs)
        if kwargs['org_id'] not in PUBLIC_COLLECTIONS.keys():
            raise Http404
        download_file = Exports.objects.filter(
            organization_id=kwargs['org_id'],
            title=PUBLIC_IMAGES_EXPORT_TITLE).order_by('date_added').last()
        example = None
        example_img = SpecimenImage.objects.filter(
            id=PUBLIC_COLLECTIONS[kwargs['org_id']]['example_img_id']).first()
        if example_img:
            example = {
                'img_captioned': get_img_captioned(
                    example_img.image_thumbnail_medium,
                    example_img.specimen.classification.gbif_canonical_name),
                'details': example_img,
                'location': get_specimen_location(example_img.specimen),
                'species': example_img.specimen.classification.gbif_species
                if example_img.specimen.classification.gbif_species
                else example_img.specimen.classification.gbif_genus + ' spp.'
            }

        context.update({
            'download_link': get_media_url(download_file.file),
            'file_size': download_file.file.size,
            'description': download_file.description,
            'example': example,
            'collection': PUBLIC_COLLECTIONS[self.kwargs['org_id']]
        })
        return context
