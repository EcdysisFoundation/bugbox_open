"""Link growers to sample codes for results and uploads"""

from __future__ import annotations

import re
from dataclasses import dataclass

from django.contrib.auth import get_user_model
from django.db import transaction

from bugbox3.grower_portal.models import GrowerSampleCodeMapping, SampleCode, SiteTransect

User = get_user_model()


@dataclass
class AssignGrowerSampleCodeResult:
    mapping: GrowerSampleCodeMapping
    mapping_created: bool
    sample_code_created: bool
    year_updated: bool
    site_transects_created: int


def ensure_ignite_site_transects(sample_code: SampleCode) -> int:
    """Create T1–T4 SiteTransect rows for an Ignite site code"""
    if sample_code.project_type != 'ignite':
        return 0
    existing = set(
        SiteTransect.objects.filter(site_code=sample_code).values_list('transect_number', flat=True)
    )
    created = 0
    for t_num in range(1, 5):
        if t_num not in existing:
            SiteTransect.objects.create(
                site_code=sample_code,
                transect_number=t_num,
                is_active=True,
            )
            created += 1
    return created


def resolve_or_create_sample_code(
    *,
    code: str,
    project_type: str,
    created_by,
) -> tuple[SampleCode, bool]:
    """
    Return (SampleCode, created) and raises ValueError if code exists with a different project_type
    """
    code = code.strip()
    if not code:
        raise ValueError('Site code is required.')

    try:
        sample_code = SampleCode.objects.get(code=code)
    except SampleCode.DoesNotExist:
        site_code_numeric = None
        if project_type == 'ignite':
            numeric_match = re.search(r'\d+', code)
            if numeric_match:
                site_code_numeric = int(numeric_match.group())
        sample_code = SampleCode.objects.create(
            code=code,
            project_type=project_type,
            site_code_numeric=site_code_numeric,
            created_by=created_by,
            is_active=True,
        )
        return sample_code, True

    if sample_code.project_type != project_type:
        raise ValueError(
            f'Sample code "{code}" already exists as {sample_code.get_project_type_display()} '
            f'({sample_code.project_type}), not {project_type}.'
        )
    return sample_code, False


@transaction.atomic
def assign_grower_sample_code_mapping(
    *,
    grower,
    site_code: str,
    year_sampled: int,
    project_type: str,
    created_by,
) -> AssignGrowerSampleCodeResult:
    sample_code, sample_code_created = resolve_or_create_sample_code(
        code=site_code,
        project_type=project_type,
        created_by=created_by,
    )
    site_transects_created = ensure_ignite_site_transects(sample_code)

    mapping, mapping_created = GrowerSampleCodeMapping.objects.get_or_create(
        grower=grower,
        sample_code=sample_code,
        defaults={'year_sampled': year_sampled},
    )
    year_updated = False
    if not mapping_created and mapping.year_sampled != year_sampled:
        mapping.year_sampled = year_sampled
        mapping.save(update_fields=['year_sampled'])
        year_updated = True

    return AssignGrowerSampleCodeResult(
        mapping=mapping,
        mapping_created=mapping_created,
        sample_code_created=sample_code_created,
        year_updated=year_updated,
        site_transects_created=site_transects_created,
    )
