from django.conf import settings

from bugbox3.core.constants import FIPS_STATE
from bugbox3.grower_portal.constants import (
    GOOGLE_MAPS_CALLBACK_INTERACTIVE,
    GOOGLE_MAPS_CALLBACK_READONLY,
    GOOGLE_MAPS_VERSION,
)
from bugbox3.libs.utilities import get_json_context


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


def build_interactive_transect_data(application, default_latitude, default_longitude):
    """Build transect map payload"""
    transect_data = []
    for slot in range(1, 5):
        code = getattr(application, f'transect_code_{slot}', None)
        if not code:
            continue
        location = getattr(application, f'transect_{slot}_location', None)
        if location:
            latitude = float(location.y)
            longitude = float(location.x)
        else:
            latitude = default_latitude
            longitude = default_longitude
        transect_data.append({
            'index': slot - 1,
            'slot': slot,
            'code': code,
            'latitude': latitude,
            'longitude': longitude,
        })
    return transect_data


def get_grower_maps_json_context(
    transect_data,
    *,
    callback=GOOGLE_MAPS_CALLBACK_READONLY,
    field_latitude=None,
    field_longitude=None,
):
    payload = {
        'transectData': transect_data,
        'googleMapsApiKey': settings.GOOGLE_MAPS_API_KEY,
        'googleMapsCallback': callback,
        'googleMapsVersion': GOOGLE_MAPS_VERSION,
    }
    if field_latitude is not None:
        payload['fieldLatitude'] = field_latitude
    if field_longitude is not None:
        payload['fieldLongitude'] = field_longitude
    return get_json_context(payload)


def get_grower_maps_json_context_interactive(transect_data, field_latitude, field_longitude):
    return get_grower_maps_json_context(
        transect_data,
        callback=GOOGLE_MAPS_CALLBACK_INTERACTIVE,
        field_latitude=field_latitude,
        field_longitude=field_longitude,
    )
