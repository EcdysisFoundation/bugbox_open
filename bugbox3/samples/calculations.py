import math


def get_indices(n, row, non_species_keys):
    shannons_h = 0
    simpsons = 0
    hill_shannon = 0
    hill_simpson = 0
    species_count = 0

    for k, v in row.items():
        if k not in non_species_keys:
            if v:
                species_count += 1
            if n and v:
                shannons_h -= (v / n) * math.log(v / n)
            if n > 1:
                simpsons += v * (v - 1)
            if n:
                hill_simpson += (v / n) ** 2
    if n > 1:
        simpsons = 1 - (simpsons / (n * (n - 1)))
    if hill_simpson:
        hill_simpson = 1 / hill_simpson
    return {
        'abundance': n,
        'species_richness': species_count,
        'shannons_h': math.exp(shannons_h),
        'simpsons': simpsons,
        'hill_shannon': hill_shannon,
        'hill_simpson': hill_simpson
    }
