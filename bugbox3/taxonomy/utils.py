from django.db.models import Q

from . import constants
from .models import Morphospecies


def get_skip_morphospecies_ids():
    phylums = [
        v[constants.FIELD_MORPHO_GBIF_PHYLUM] for v in constants.SKIP_MORPHOSPECIES
        if constants.FIELD_MORPHO_GBIF_PHYLUM in v
    ]
    classes = [
        v[constants.FIELD_MORPHO_GBIF_CLASS] for v in constants.SKIP_MORPHOSPECIES
        if constants.FIELD_MORPHO_GBIF_CLASS in v
    ]
    orders = [
        v[constants.FIELD_MORPHO_GBIF_ORDER] for v in constants.SKIP_MORPHOSPECIES
        if constants.FIELD_MORPHO_GBIF_ORDER in v
    ]
    names = [v[constants.FIELD_MORPHO_NAME] for v in constants.SKIP_MORPHOSPECIES]
    return list(Morphospecies.objects.filter(
        Q(gbif_phylum__in=phylums) |
        Q(gbif_class__in=classes) |
        Q(gbif_order__in=orders) |
        Q(name__in=names)
    ).values_list('id', flat=True))


def get_immature_morphospecies_ids():
    return list(
        Morphospecies.objects.filter(
            Q(name__icontains="immature")
        ).values_list("id", flat=True)
    )
