from bugbox3.core.constants import FIPS_STATE


def state_name_to_abbreviation(state_name):
    """
    Convert full state name to abbreviation, takes full state name and returns abbreviation.
    """
    if not state_name:
        return state_name

    state_name = state_name.strip()

    if len(state_name) == 2 and state_name.isupper():
        return state_name

    state_name_mapping = {
        'alabama': 'AL',
        'alaska': 'AK',
        'arizona': 'AZ',
        'arkansas': 'AR',
        'california': 'CA',
        'colorado': 'CO',
        'connecticut': 'CT',
        'delaware': 'DE',
        'district of columbia': 'DC',
        'florida': 'FL',
        'georgia': 'GA',
        'hawaii': 'HI',
        'idaho': 'ID',
        'illinois': 'IL',
        'indiana': 'IN',
        'iowa': 'IA',
        'kansas': 'KS',
        'kentucky': 'KY',
        'louisiana': 'LA',
        'maine': 'ME',
        'maryland': 'MD',
        'massachusetts': 'MA',
        'michigan': 'MI',
        'minnesota': 'MN',
        'mississippi': 'MS',
        'missouri': 'MO',
        'montana': 'MT',
        'nebraska': 'NE',
        'nevada': 'NV',
        'new hampshire': 'NH',
        'new jersey': 'NJ',
        'new mexico': 'NM',
        'new york': 'NY',
        'north carolina': 'NC',
        'north dakota': 'ND',
        'ohio': 'OH',
        'oklahoma': 'OK',
        'oregon': 'OR',
        'pennsylvania': 'PA',
        'rhode island': 'RI',
        'south carolina': 'SC',
        'south dakota': 'SD',
        'tennessee': 'TN',
        'texas': 'TX',
        'utah': 'UT',
        'vermont': 'VT',
        'virginia': 'VA',
        'washington': 'WA',
        'west virginia': 'WV',
        'wisconsin': 'WI',
        'wyoming': 'WY',
    }

    state_lower = state_name.lower()
    if state_lower in state_name_mapping:
        return state_name_mapping[state_lower]

    if state_name.upper() in FIPS_STATE.values():
        return state_name.upper()

    return state_name
