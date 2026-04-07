from django.db.models import Q

from . import constants
from .constants import FIELD_MORPHO_GBIF_KEY, MORPHOSPECIES_TAXONOMY_REVIEW_FIELDS
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


def _norm_taxonomy_value(field_name, value):
    if field_name == FIELD_MORPHO_GBIF_KEY:
        return value
    if value is None:
        return ''
    return (str(value) or '').strip()


def morphospecies_taxonomy_fields_changed(before, after) -> bool:
    """Return True if any MORPHOSPECIES_TAXONOMY_REVIEW_FIELDS value differs between instances."""
    for fname in MORPHOSPECIES_TAXONOMY_REVIEW_FIELDS:
        old_v = _norm_taxonomy_value(fname, getattr(before, fname))
        new_v = _norm_taxonomy_value(fname, getattr(after, fname))
        if old_v != new_v:
            return True
    return False
