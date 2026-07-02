"""Map scientific functional-group traits to grower ecological role buckets"""

from __future__ import annotations

GROWER_BUCKET_TRAITS: dict[str, tuple[str, ...]] = {
    'herbivore': ('phytophagous',),
    'natural_enemy': ('predator', 'parasitoid'),
    'detritivore': ('detritophagous', 'mycetophagous', 'coprophagous', 'necrophagous'),
    'pollinator': ('pollinator',),
}


def scientific_traits_to_grower_weights(traits: dict[str, bool]) -> dict[str, float] | None:
    """even split across grower buckets that have any active mapped trait"""
    active_buckets = [
        bucket
        for bucket, codes in GROWER_BUCKET_TRAITS.items()
        if any(traits.get(code) for code in codes)
    ]
    if not active_buckets:
        return None
    share = 1.0 / len(active_buckets)
    return {bucket: share for bucket in active_buckets}


def build_grower_weights_cache(
    traits_by_morpho_id: dict[int, dict[str, bool]],
) -> dict[int, dict[str, float]]:
    return {
        morpho_id: weights
        for morpho_id, traits in traits_by_morpho_id.items()
        if (weights := scientific_traits_to_grower_weights(traits)) is not None
    }
