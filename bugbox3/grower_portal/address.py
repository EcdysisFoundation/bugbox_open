"""Grower mailing address validation."""

ADDRESS_COMPONENT_FIELDS = (
    'address_line',
    'address_line_2',
    'city',
    'state',
    'county',
    'postal_code',
)


def strip_address_fields(cleaned_data):
    for field in ADDRESS_COMPONENT_FIELDS:
        cleaned_data[field] = (cleaned_data.get(field) or '').strip()
    cleaned_data['country'] = (cleaned_data.get('country') or '').strip()
    return cleaned_data


def validate_grower_address(cleaned_data):

    strip_address_fields(cleaned_data)

    components = {field: cleaned_data[field] for field in ADDRESS_COMPONENT_FIELDS}
    country = cleaned_data['country']

    has_any = bool(country) or any(components.values())
    if not has_any:
        return {}

    errors = {}

    if not country:
        errors['country'] = 'Please select a country when providing an address.'
    if not components['city']:
        errors['city'] = 'Please enter a city or town when providing an address.'
    if (components['state'] or components['county']) and not components['address_line']:
        errors['address_line'] = (
            'Please enter a street address when providing a state/province or county.'
        )
    if components['address_line_2'] and not components['address_line']:
        errors['address_line'] = 'Please enter a street address when providing an apartment or unit.'

    return errors
