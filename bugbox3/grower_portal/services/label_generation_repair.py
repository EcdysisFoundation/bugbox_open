"""
Repair label generations stuck in queued/processing
"""

from __future__ import annotations

from typing import Literal

from ..models import LabelGeneration

RepairAction = Literal['marked_ready', 'requeue', 'cannot']


def ensure_generation_params(gen: LabelGeneration) -> dict:
    """
    Build or complete generation_params from the LabelGeneration row (for pre-async records).
    """
    params = dict(gen.generation_params or {})
    codes = [str(c).strip() for c in (gen.transect_codes_generated or []) if str(c).strip()]

    if gen.label_category == 'inner':
        sample_types = params.get('sample_types') or list(gen.sample_types or [])
        if gen.project_type == 'ignite':
            n_sites = params.get('number_of_transects')
            if not n_sites:
                n_sites = gen.labels_per_type if gen.labels_per_type else len(codes)
            if not n_sites and codes:
                n_sites = len(codes)
            params.setdefault('number_of_transects', int(n_sites or 0))
            params.setdefault('sample_types', sample_types)
            params.setdefault('labels_per_type', 4)
        else:
            n_transects = params.get('number_of_transects')
            if not n_transects:
                n_transects = gen.labels_per_type if gen.labels_per_type else len(codes)
            if not n_transects and codes:
                n_transects = len(codes)
            params.setdefault('number_of_transects', int(n_transects or 0))
            params.setdefault('sample_types', sample_types)
            params.setdefault('labels_per_type', int(n_transects or 0))
    else:
        if gen.project_type == 'ignite':
            params.setdefault('sample_types', params.get('sample_types') or list(gen.sample_types or []))
            params.setdefault('labels_per_type', 1)
            params.setdefault('site_codes', params.get('site_codes') or codes)
        else:
            params.setdefault('transect_codes', params.get('transect_codes') or codes)
            params.setdefault('labels_per_type', 0)
            params.setdefault('sample_types', [])

    return params


def can_retry_label_generation(gen: LabelGeneration) -> tuple[bool, str]:
    if gen.status == 'ready':
        return False, 'This generation is already ready.'

    if gen.label_file:
        return True, ''

    params = ensure_generation_params(gen)
    codes = [str(c).strip() for c in (gen.transect_codes_generated or []) if str(c).strip()]

    if codes:
        return True, ''

    if gen.label_category == 'inner':
        n = int(params.get('number_of_transects') or 0)
        if n > 0 and (params.get('sample_types') or gen.sample_types):
            return True, ''

    if gen.label_category == 'outer':
        if gen.project_type == 'ignite' and params.get('site_codes'):
            return True, ''
        if gen.project_type == 'avalanche' and params.get('transect_codes'):
            return True, ''

    return (
        False,
        'This record has no stored document, codes, or generation parameters. '
        'Create a new label generation from Label Management instead.',
    )


def prepare_label_generation_retry(gen: LabelGeneration) -> tuple[RepairAction, str]:
    """
    Update ``gen`` for retry. Returns action taken and a short user-facing detail string.

    Caller must enqueue Celery when action is ``requeue``.
    """
    ok, reason = can_retry_label_generation(gen)
    if not ok:
        raise ValueError(reason)

    if gen.label_file:
        gen.status = 'ready'
        gen.error_message = ''
        gen.save(update_fields=['status', 'error_message'])
        return 'marked_ready', 'Status set to Ready (document was already on file).'

    params = ensure_generation_params(gen)
    codes = [str(c).strip() for c in (gen.transect_codes_generated or []) if str(c).strip()]
    if codes:
        params['reuse_transect_codes'] = True

    gen.generation_params = params
    gen.status = 'queued'
    gen.error_message = ''
    gen.save(update_fields=['generation_params', 'status', 'error_message'])

    if codes:
        detail = f'Queued regeneration using {len(codes)} stored code(s).'
    else:
        detail = 'Queued label generation using saved parameters.'
    return 'requeue', detail
