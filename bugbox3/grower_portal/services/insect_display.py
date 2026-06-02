"""Grower display labels for bug results"""

from bugbox3.grower_portal.constants import (
    GROWER_FAMILY_DISPLAY_FALLBACK,
    GROWER_MORPHO_FAMILY_DISPLAY,
)
from bugbox3.samples.export_metrics import UNKNOWN_TAXON, UNSPECIFIED_FAMILY
from bugbox3.taxonomy.models import Morphospecies


def display_family_for_grower(morpho: Morphospecies | None) -> str:
    """
    family label for grower Bugs UI
    """
    if not morpho:
        return UNKNOWN_TAXON
    if morpho.gbif_family:
        return morpho.gbif_family
    return GROWER_MORPHO_FAMILY_DISPLAY.get(morpho.name, GROWER_FAMILY_DISPLAY_FALLBACK)
