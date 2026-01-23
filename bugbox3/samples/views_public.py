from django.http import Http404
from django.views.generic import TemplateView
from rest_framework.reverse import reverse as api_reverse

from ..core.models import Exports, PrivateSiteContent
from ..libs.ui_helpers import get_img_captioned, get_specimen_location
from ..libs.utilities import get_json_context, get_media_url
from ..samples.exports import PUBLIC_ALL_IMAGES_EXPORT_TITLE, PUBLIC_IMAGES_EXPORT_TITLE
from ..samples.models import SpecimenImage
from ..taxonomy import constants as constants_tax
from ..taxonomy.models_query import get_taxon_entries

# These can become entries in the Organization model when more orgs have public data.
ECDYSIS_COLLECTION = 'The Mark F. Longfellow Ecological Reference Collection'
PUBLIC_DATA_ORGS = [(1, 'Ecdysis Foundation'), ]
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
        all_download_file = Exports.objects.filter(
            organization_id=kwargs['org_id'],
            title=PUBLIC_ALL_IMAGES_EXPORT_TITLE).order_by('date_added').last()
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
        metaformer_zip = PrivateSiteContent.objects.filter(
            title__icontains='metaformer-version',
            file__icontains='.zip').last()

        context.update({
            'download_link': get_media_url(download_file.file)
            if download_file else '',
            'download_date_added': download_file.date_added if download_file else '',
            'file_size': download_file.file_size if download_file else '',
            'description': download_file.description if download_file else '',
            'all_download_link': get_media_url(all_download_file.file)
            if all_download_file else '',
            'all_file_size': all_download_file.file_size if all_download_file else '',
            'all_description': all_download_file.description if all_download_file else '',
            'all_download_date_added': all_download_file.date_added if all_download_file else '',
            'example': example,
            'collection': PUBLIC_COLLECTIONS[self.kwargs['org_id']],
            'metaformer_zip_link': get_media_url(metaformer_zip.file) if metaformer_zip else '',
            'metaformer_zip_file_size': metaformer_zip.file_size if metaformer_zip else '',
            'metaformer_zip_description': metaformer_zip.description if metaformer_zip else ''
        })
        return context
