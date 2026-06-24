"""Kelton CSV import helpers only. Safe to remove after production import."""

from __future__ import annotations

import csv
from pathlib import Path

# CSV header to FunctionalGroup.code
CSV_COLUMN_TO_CODE: dict[str, str] = {
    'sap-sucking': 'sap_sucking',
    'stem-feeding': 'stem_feeding',
    'flower-feeding': 'flower_feeding',
    'fruit/seed-feeding': 'fruit_seed_feeding',
    'gall-inducing': 'gall_inducing',
    'leaf miners': 'leaf_miners',
    'root-feeding': 'root_feeding',
    'algae/moss-feeding': 'algae_moss_feeding',
}

IMPORTABLE_CSV_COLUMNS: tuple[str, ...] = (
    'young_terrestrial',
    'young_aquatic',
    'adult_terrestrial',
    'adult_aquatic',
    'phytophagous',
    'zoophagous',
    'mycetophagous',
    'detritophagous',
    'coprophagous',
    'pollinator',
    'phyllophagous',
    'saproxylic',
    'sap-sucking',
    'stem-feeding',
    'flower-feeding',
    'fruit/seed-feeding',
    'gall-inducing',
    'leaf miners',
    'root-feeding',
    'algae/moss-feeding',
    'predator',
    'micropredator',
    'parasite',
    'parasitoid',
    'necrophagous',
)


def csv_column_to_code(column: str) -> str:
    return CSV_COLUMN_TO_CODE.get(column, column)


def parse_csv_weight(value: str) -> float | None:
    text = str(value).strip()
    if not text:
        return None
    try:
        weight = float(text)
    except ValueError:
        return None
    if weight <= 0:
        return None
    return weight


def row_to_trait_weights(row: dict[str, str]) -> dict[str, float]:
    weights: dict[str, float] = {}
    for column in IMPORTABLE_CSV_COLUMNS:
        weight = parse_csv_weight(row.get(column, ''))
        if weight is not None:
            weights[csv_column_to_code(column)] = weight
    return weights


def read_functional_groups_csv(path: Path) -> list[dict]:
    with path.open(newline='', encoding='utf-8') as handle:
        return list(csv.DictReader(handle))
