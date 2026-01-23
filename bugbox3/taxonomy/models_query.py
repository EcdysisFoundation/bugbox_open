from django.db.models import Count

from ..samples.models import Specimen


def get_taxon_entries(org_id, col, public_image=False):
    """
    Get a list of choices for orders based on org data.
    """
    col = 'classification__' + col
    v = Specimen.objects.filter(
        sample__site_visit__site__experiment__organization_id=org_id
    )
    if public_image:
        v = v.filter(specimenimage__public_image=True)
    v = v.exclude(acceptance=0).values(col).annotate(count=Count(col)).order_by()
    return [(i, d[col], d['count']) for i, d in enumerate(v, start=1) if d[col]]
