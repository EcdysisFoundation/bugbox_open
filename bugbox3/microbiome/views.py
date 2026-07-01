from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import F
from django.urls import reverse
from django.views.generic import TemplateView

from bugbox3.core.permissions import IS_GROWER_USER
from bugbox3.grower_portal.models import GrowerSampleCodeMapping
from bugbox3.libs.utilities import get_media_url

from . import constants
from .models import SiteMicrobiomeTaxa


def _grower_sample_code_ids(grower):
    grower_id = grower.id if hasattr(grower, 'id') else grower
    return GrowerSampleCodeMapping.objects.filter(
        grower_id=grower_id,
    ).values_list('sample_code_id', flat=True)


def get_microbiome_available_years(grower):
    sample_codes = _grower_sample_code_ids(grower)
    years = (
        SiteMicrobiomeTaxa.objects.filter(grower_site_code_id__in=sample_codes)
        .values_list('sample_year', flat=True)
        .distinct()
    )
    return sorted(set(years) - {None}, reverse=True)


def grower_has_microbiome_data(grower, year):
    sample_codes = _grower_sample_code_ids(grower)
    qs = SiteMicrobiomeTaxa.objects.filter(grower_site_code_id__in=sample_codes)
    if year is not None:
        qs = qs.filter(sample_year=year)
    return qs.exists()


def get_site_microbiome_taxa_context(user_id, year=None):
    sample_codes = _grower_sample_code_ids(user_id)
    qs = SiteMicrobiomeTaxa.objects.filter(grower_site_code_id__in=sample_codes)
    if year is not None:
        qs = qs.filter(sample_year=year)
    site_data = list(
        qs.annotate(target_region=F('parent_file__target_region'))
        .order_by('site_code', 'target_region', 'analytics_sample_id')
        .values()
    )
    if not site_data:
        return
    for s in site_data:
        s['organism_description'] = constants.TARGET_COMMON_NAME.get(
            s['target_region'], 'Unknown'
        )
        s['download_url'] = get_media_url(s['user_file'])
    return {
        'site_data': site_data,
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
            years = sorted(
                {row['sample_year'] for row in context_data['site_data'] if row.get('sample_year')},
                reverse=True,
            )
            context['microbiome_results_year'] = years[0] if years else None
        context['grower_results_url'] = reverse('grower_portal:results')
        return context
