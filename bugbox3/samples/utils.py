from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db.models import Count
from django.utils import timezone
import logging

from bugbox3.samples.models import SpecimenImage, MultiSpecimenImage

User = get_user_model()
logger = logging.getLogger(__name__)

def get_user_display(user_id):
    try:
        u = User.objects.get(id=user_id)
        if u.name and u.name.strip():
            parts = u.name.strip().split()
            first = parts[0]
            last_initial = f" {parts[1][0].upper()}" if len(parts) > 1 and parts[1] else ''
            return f"{first}{last_initial}"
        elif u.username:
            return u.username
        elif u.email:
            return u.email
        else:
            return "Unknown"
    except User.DoesNotExist:
        return "Unknown"


def resolve_entered_by(sample):
    specimen_uploader = (
        SpecimenImage.objects
        .filter(specimen__sample=sample, uploaded_by_user__isnull=False)
        .values('uploaded_by_user')
        .annotate(count=Count('id'))
        .order_by('-count')
        .first()
    )

    multi_uploader = (
        MultiSpecimenImage.objects
        .filter(sample=sample, uploaded_by_user__isnull=False)
        .values('uploaded_by_user')
        .annotate(count=Count('id'))
        .order_by('-count')
        .first()
    )

    if specimen_uploader and multi_uploader:
        if specimen_uploader['count'] >= multi_uploader['count']:
            return get_user_display(specimen_uploader['uploaded_by_user'])
        else:
            return get_user_display(multi_uploader['uploaded_by_user'])
    elif specimen_uploader:
        return get_user_display(specimen_uploader['uploaded_by_user'])
    elif multi_uploader:
        return get_user_display(multi_uploader['uploaded_by_user'])
    elif sample.created_by_user:
        return get_user_display(sample.created_by_user.id)
    elif getattr(sample.site_visit.site, 'created_by', None):
        return get_user_display(sample.site_visit.site.created_by.id)
    else:
        return "Unknown"


def get_specimen_context_cached(specimen):

    try:
        if hasattr(specimen, 'site_name') and hasattr(specimen, 'visit_date'):
            site_name = specimen.site_name
            visit_date = specimen.visit_date
            state_region = getattr(specimen, 'state_region', '')
        else:

            site_name = specimen.sample.site_visit.site.site_name if specimen.sample else ''
            visit_date = specimen.sample.site_visit.visit_date if specimen.sample else None
            state_region = specimen.sample.site_visit.site.state_region if specimen.sample else ''
        
        context_parts = []
        if site_name:
            context_parts.append(site_name)
        if visit_date:
            context_parts.append(visit_date.strftime('%Y-%m-%d'))
        if state_region:
            context_parts.append(state_region)
        
        return ' | '.join(context_parts) if context_parts else ''
        
    except Exception as e:
        logger.warning(f"Error getting specimen context for specimen {specimen.id}: {e}")
        return 'Context unavailable'


def get_safe_image_url(image_field, public=False):

    try:
        if not image_field:
            return ''
        
        from django.core.files.storage import default_storage
        from ..libs.utilities import get_media_url
        
        if not default_storage.exists(image_field.name):
            return ''
        
        return get_media_url(image_field, public=public)
    except Exception:
        return ''


def batch_prefetch_specimen_data(specimen_ids, chunk_size=1000):

    from .models import Specimen
    from django.db.models import Prefetch
    
    prefetched_data = {}
    
    for i in range(0, len(specimen_ids), chunk_size):
        chunk_ids = specimen_ids[i:i + chunk_size]
        
        try:
            specimens = Specimen.objects.filter(
                id__in=chunk_ids
            ).select_related(
                'classification',
                'ai_classification',
                'sample__site_visit__site'
            ).prefetch_related(
                Prefetch(
                    'specimenimage_set',
                    queryset=SpecimenImage.objects.select_related().order_by('-primary_image'),
                    to_attr='prefetched_images'
                )
            )
            
            for specimen in specimens:
                prefetched_data[specimen.id] = specimen
                
        except Exception as e:
            logger.error(f"Error in batch prefetch for chunk {i}-{i+chunk_size}: {e}")
            
    return prefetched_data
