from ..samples.constants import (FIELD_SAMPLE_TYPE, FIELD_SITE_HABITAT_TYPE,
                                 FIELD_SITE_TREATMENT, FIELD_SPECIMEN_TAGS)

# LookupChoices

FIELD_FIELD = 'field'
FIELD_ENTRY = 'entry'
FIELD_DISPLAY_TXT = 'display_txt'

VALID_LOOKUP_FIELDS = [
    FIELD_SITE_HABITAT_TYPE, FIELD_SITE_TREATMENT,
    FIELD_SAMPLE_TYPE, FIELD_SPECIMEN_TAGS
]

# Site

CANADA = 'Canada'
UNITED_STATES = 'United States'

US_STATE_CHOICES = 'US_STATE_CHOICES'
CANADA_STATE_CHOICES = 'CANADA_STATE_CHOICES'

COUNTRY_CHOICES = ((CANADA_STATE_CHOICES, CANADA), (US_STATE_CHOICES, UNITED_STATES))
COUNTRY_LOOKUP = {v[0]: v[1] for v in COUNTRY_CHOICES}

FIPS_STATE = {
    '02': 'AK',
    '01': 'AL',
    '05': 'AR',
    '60': 'AS',
    '04': 'AZ',
    '06': 'CA',
    '08': 'CO',
    '09': 'CT',
    '11': 'DC',
    '10': 'DE',
    '12': 'FL',
    '13': 'GA',
    '66': 'GU',
    '15': 'HI',
    '19': 'IA',
    '16': 'ID',
    '17': 'IL',
    '18': 'IN',
    '20': 'KS',
    '21': 'KY',
    '22': 'LA',
    '25': 'MA',
    '24': 'MD',
    '23': 'ME',
    '26': 'MI',
    '27': 'MN',
    '29': 'MO',
    '28': 'MS',
    '30': 'MT',
    '37': 'NC',
    '38': 'ND',
    '31': 'NE',
    '33': 'NH',
    '34': 'NJ',
    '35': 'NM',
    '32': 'NV',
    '36': 'NY',
    '39': 'OH',
    '40': 'OK',
    '41': 'OR',
    '42': 'PA',
    '72': 'PR',
    '44': 'RI',
    '45': 'SC',
    '46': 'SD',
    '47': 'TN',
    '48': 'TX',
    '49': 'UT',
    '51': 'VA',
    '78': 'VI',
    '50': 'VT',
    '53': 'WA',
    '55': 'WI',
    '54': 'WV',
    '56': 'WY'
}


STATE_CHOICES = {
    US_STATE_CHOICES: [[v, v] for _ , v in FIPS_STATE.items()],
    CANADA_STATE_CHOICES: (('Manitoba', 'Manitoba'), ('Saskatchewan', 'Saskatchewan'))
}


# Stitcher API Constants
STITCHER_PANORAMA_PATH = 'panorama_path'
STITCHER_APPROVED = 'approved'
STITCHER_GUID = 'guid'
