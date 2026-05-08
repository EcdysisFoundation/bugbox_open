"""
Outbound reference URLs for bird species (All About Birds)
"""

from __future__ import annotations

import re
from typing import Any

SPECIES_REFERENCE_OVERRIDES: dict[str, dict[str, Any]] = {

    # },
}


def _normalize_common_name(name: str) -> str:
    s = (name or "").strip()
    s = re.sub(r"\s+", " ", s)
    return s


def _aab_slug_from_name(name: str) -> str:
    """
    All About Birds guide segment: spaces -> underscores
    example: 'Red-tailed Hawk' -> 'Red-tailed_Hawk'
    """
    n = _normalize_common_name(name)
    if not n:
        return ""
    parts = n.split(" ")
    return "_".join(parts)

def build_all_about_birds_overview_url(common_name: str) -> str:
    """Build the All About Birds overview URL for a species common name."""
    name = _normalize_common_name(common_name)
    override = SPECIES_REFERENCE_OVERRIDES.get(name, {})
    aab_slug = override.get("aab_slug") or _aab_slug_from_name(name)
    if not aab_slug:
        return ""
    return f"https://www.allaboutbirds.org/guide/{aab_slug}/overview"
