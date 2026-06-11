from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import F
from django.views.generic import TemplateView

from bugbox3.core.permissions import IS_GROWER_USER
from bugbox3.grower_portal.models import GrowerSampleCodeMapping
from bugbox3.libs.utilities import get_media_url

from . import constants
from .models import SiteMicrobiomeTaxa


def get_site_microbiome_taxa_context(user_id):
    sample_codes = GrowerSampleCodeMapping.objects.filter(
        grower_id=user_id).values_list('sample_code_id', flat=True)
    site_data = list(SiteMicrobiomeTaxa.objects.filter(
        grower_site_code_id__in=sample_codes).annotate(
            target_region=F('parent_file__target_region')).values())
    if not site_data:
        return
    for s in site_data:
        s['organism_description'] = constants.TARGET_COMMON_NAME.get(
            s['target_region'], 'Unknown'
        )
        s['download_url'] = get_media_url(s['user_file'])
    return {
        'site_data': site_data
    }


class SiteMicrobiomeTaxaView(PermissionRequiredMixin, TemplateView):

    permission_required = IS_GROWER_USER
    template_name = 'microbiome/site_microbiome.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.request.user.id
        context_data = get_site_microbiome_taxa_context(user_id)
        if context_data:
            context.update(context_data)
        return context
