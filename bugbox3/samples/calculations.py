import math


def get_indices(n, row, non_species_keys):
    if n == 0:
        return {
            'abundance': 0,
            'species_richness': 0,
            'shannons_h': 'N/A',
            'simpsons_d': 'N/A',
            'simpsons_d_prime': 'N/A',
            'gini_simpson': 'N/A',
            'hill_H0': 'N/A',
            'hill_H1': 'N/A',
            'hill_H2': 'N/A',
            'hill_inf': 'N/A',
            'chao1': 'N/A',
            'absolute_effective_diversity': 'N/A'
        }

    shannons_h = 0
    simpsons_d = 0
    simpsons_d_prime = 0
    gini_simpson = 0
    hill_numbers = {}
    species_count = 0
    n1 = n2 = 0
    max_abundance = 0
    total_squared = 0

    for k, v in row.items():
        if k not in non_species_keys and v:
            species_count += 1
            if v == 1:
                n1 += 1
            elif v == 2:
                n2 += 1
            max_abundance = max(max_abundance, v)
            if n:
                shannons_h -= (v / n) * math.log(v / n)
                total_squared += (v / n) ** 2
            if n > 1:
                simpsons_d_prime += v * (v - 1)

    simpsons_d = total_squared
    simpsons_d_prime = simpsons_d_prime / (n * (n - 1)) if n > 1 else 0

    gini_simpson = 1 - simpsons_d

    hill_numbers['H0'] = species_count
    hill_numbers['H1'] = math.exp(shannons_h)
    hill_numbers['H2'] = 1 / simpsons_d if simpsons_d else 0
    hill_numbers['H∞'] = n / max_abundance if max_abundance else 0
    aed = hill_numbers['H0'] + (hill_numbers['H1'] ** 2) / (2 * hill_numbers['H2'])
    return {
        'abundance': n,
        'species_richness': species_count,
        'shannons_h': shannons_h if n > 0 else 'N/A',
        'simpsons_d': simpsons_d if n > 0 else 'N/A',
        'simpsons_d_prime': simpsons_d_prime if n > 0 else 'N/A',
        'gini_simpson': gini_simpson if n > 0 else 'N/A',
        'hill_H0': species_count if n > 0 else 'N/A',
        'hill_H1': hill_numbers['H1'] if n > 0 else 'N/A',
        'hill_H2': hill_numbers['H2'] if n > 0 else 'N/A',
        'hill_inf': hill_numbers['H∞'] if n > 0 else 'N/A',
        'chao1': species_count + (n1 * (n1 - 1)) / (2 * (n2 + 1)) if n2 > 0 else species_count,
        'absolute_effective_diversity': aed if n > 0 else 'N/A'
    }
