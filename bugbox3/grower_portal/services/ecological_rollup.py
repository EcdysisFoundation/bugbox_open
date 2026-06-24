"""Map scientific functional-group traits to grower ecological role buckets"""

from __future__ import annotations

GROWER_BUCKET_TRAITS: dict[str, tuple[str, ...]] = {
    'herbivore': ('phytophagous',),
    'natural_enemy': ('predator', 'parasitoid'),
    'detritivore': ('detritophagous', 'mycetophagous', 'coprophagous', 'necrophagous'),
    'pollinator': ('pollinator',),
}


def normalize_weights(raw: dict[str, float]) -> dict[str, float] | None:
    active = {key: value for key, value in raw.items() if value > 0}
    if not active:
        return None
    total = sum(active.values())
    if total <= 0:
        return None
    return {key: value / total for key, value in active.items()}


def scientific_traits_to_grower_weights(trait_weights: dict[str, float]) -> dict[str, float] | None:
    raw: dict[str, float] = {}
    for bucket, codes in GROWER_BUCKET_TRAITS.items():
        total = sum(trait_weights.get(code, 0) or 0 for code in codes)
        if total > 0:
            raw[bucket] = total
    return normalize_weights(raw)


def build_grower_weights_cache(
    trait_weights_by_morpho_id: dict[int, dict[str, float]],
) -> dict[int, dict[str, float]]:
    return {
        morpho_id: weights
        for morpho_id, traits in trait_weights_by_morpho_id.items()
        if (weights := scientific_traits_to_grower_weights(traits)) is not None
    }
