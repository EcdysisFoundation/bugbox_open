"""race legacy data migration mapping"""

from .constants import RACE_CHOICES

RACE_INDIGENOUS = 'indigenous_first_nations_native'
RACE_ANOTHER_BACKGROUND = 'another_background'
RACE_PREFER_NOT_TO_SAY = 'prefer_not_to_say'

# Old US OMB-style values -> (new race value, indigenous country code or None)
LEGACY_RACE_MAPPING = {
    'american_indian_alaska_native': (RACE_INDIGENOUS, 'US'),
    'asian': ('east_southeast_asian', None),
    'black_african_american': ('black_african_diaspora', None),
    'native_hawaiian_pacific_islander': ('pacific_islander', None),
    'white': ('white_european', None),
    'two_or_more_races': ('multiple_backgrounds', None),
    'prefer_not_to_say': (RACE_PREFER_NOT_TO_SAY, None),
}

NEW_RACE_VALUES = {value for value, _ in RACE_CHOICES}
