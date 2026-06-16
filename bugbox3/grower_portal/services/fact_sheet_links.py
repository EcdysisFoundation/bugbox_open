"""resolve grower results fact sheet PDFs from PublicSiteContent"""

from __future__ import annotations

from functools import lru_cache

from bugbox3.core.models import PublicSiteContent

from ..constants import CATEGORY_FACT_SHEETS


@lru_cache(maxsize=1)
def _fact_sheet_url_by_slug() -> dict[str, str]:
    slugs = {
        entry['slug']
        for entries in CATEGORY_FACT_SHEETS.values()
        for entry in entries
    }
    if not slugs:
        return {}

    url_by_slug: dict[str, str] = {}
    for content in PublicSiteContent.objects.filter(title__in=slugs):
        if content.file:
            url_by_slug[content.title] = content.file.url
    return url_by_slug


def get_category_fact_sheets(category: str) -> list[dict[str, str]]:
    """return fact sheet links for a results category"""
    entries = CATEGORY_FACT_SHEETS.get(category, [])
    if not entries:
        return []

    url_by_slug = _fact_sheet_url_by_slug()
    sheets: list[dict[str, str]] = []
    for entry in entries:
        url = url_by_slug.get(entry['slug'])
        if url:
            sheets.append({'label': entry['label'], 'url': url})
    return sheets
