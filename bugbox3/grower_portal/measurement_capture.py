from .constants import (
    DEFAULT_AREA_UNIT,
    DEFAULT_DEPTH_UNIT,
    DEFAULT_TIME_UNIT,
    DEFAULT_WEIGHT_UNIT,
)
from .measurement_units import _quantize, _to_decimal, to_cm, to_days, to_hectares, to_kg


def _entered_decimal(value):
    if value in (None, ''):
        return None
    return _quantize(_to_decimal(value))


def capture_area_measurement(
    cleaned_data,
    *,
    value_key,
    unit_key,
    entered_key,
    canonical_key,
    empty_canonical=None,
):
    """Store grower-entered area and a canonical hectares value."""
    entered = cleaned_data.get(value_key)
    unit = cleaned_data.get(unit_key) or DEFAULT_AREA_UNIT

    if entered in (None, ''):
        cleaned_data[entered_key] = None
        cleaned_data[unit_key] = unit
        cleaned_data[canonical_key] = empty_canonical
        return cleaned_data

    entered_decimal = _entered_decimal(entered)
    canonical = to_hectares(entered_decimal, unit)
    cleaned_data[entered_key] = entered_decimal
    cleaned_data[unit_key] = unit
    cleaned_data[canonical_key] = canonical
    cleaned_data[value_key] = entered_decimal
    return cleaned_data


def capture_depth_measurement(cleaned_data, *, value_key, unit_key, entered_key, canonical_key):
    entered = cleaned_data.get(value_key)
    unit = cleaned_data.get(unit_key) or DEFAULT_DEPTH_UNIT

    if entered in (None, ''):
        cleaned_data[entered_key] = None
        cleaned_data[unit_key] = unit
        cleaned_data[canonical_key] = None
        return cleaned_data

    entered_decimal = _entered_decimal(entered)
    canonical = to_cm(entered_decimal, unit)
    cleaned_data[entered_key] = entered_decimal
    cleaned_data[unit_key] = unit
    cleaned_data[canonical_key] = canonical
    cleaned_data[value_key] = entered_decimal
    return cleaned_data


def capture_weight_measurement(cleaned_data, *, value_key, unit_key, entered_key, canonical_key):
    entered = cleaned_data.get(value_key)
    unit = cleaned_data.get(unit_key) or DEFAULT_WEIGHT_UNIT

    if entered in (None, ''):
        cleaned_data[entered_key] = None
        cleaned_data[unit_key] = unit
        cleaned_data[canonical_key] = None
        return cleaned_data

    entered_decimal = _entered_decimal(entered)
    cleaned_data[entered_key] = entered_decimal
    cleaned_data[unit_key] = unit
    cleaned_data[canonical_key] = to_kg(entered_decimal, unit)
    cleaned_data[value_key] = entered_decimal
    return cleaned_data


def capture_duration_measurement(cleaned_data, *, value_key, unit_key, entered_key, canonical_key):
    entered = cleaned_data.get(value_key)
    unit = cleaned_data.get(unit_key) or DEFAULT_TIME_UNIT

    if entered in (None, ''):
        cleaned_data[entered_key] = None
        cleaned_data[unit_key] = unit
        cleaned_data[canonical_key] = None
        return cleaned_data

    entered_decimal = _entered_decimal(entered)
    cleaned_data[entered_key] = entered_decimal
    cleaned_data[unit_key] = unit
    cleaned_data[canonical_key] = to_days(entered_decimal, unit)
    cleaned_data[value_key] = cleaned_data[canonical_key]
    return cleaned_data


def area_form_initial(canonical_value, entered_value, unit_value):
    unit = unit_value or DEFAULT_AREA_UNIT
    if entered_value is not None:
        return entered_value, unit
    if canonical_value is not None:
        from .measurement_units import from_hectares, parse_stored_numeric

        parsed = parse_stored_numeric(canonical_value)
        if parsed is not None:
            return from_hectares(parsed, unit), unit
    return None, unit


def depth_form_initial(canonical_value, entered_value, unit_value):
    unit = unit_value or DEFAULT_DEPTH_UNIT
    if entered_value is not None:
        return entered_value, unit
    if canonical_value not in (None, ''):
        from .measurement_units import from_cm, parse_stored_numeric

        parsed = parse_stored_numeric(canonical_value)
        if parsed is not None:
            return from_cm(parsed, unit), unit
    return None, unit


def assign_field_measurements(field, cleaned_data):
    field.area_sampled_ha = cleaned_data.get('area_sampled_ha')
    field.area_sampled_entered = cleaned_data.get('area_sampled_entered')
    field.area_sampled_unit = cleaned_data.get('area_sampled_unit') or DEFAULT_AREA_UNIT
    field.paddock_size_ha = cleaned_data.get('paddock_size_ha')
    field.paddock_size_entered = cleaned_data.get('paddock_size_entered')
    field.paddock_size_unit = cleaned_data.get('paddock_size_unit') or DEFAULT_AREA_UNIT


def field_measurement_initial(field):
    area_value, area_unit = area_form_initial(
        field.area_sampled_ha,
        field.area_sampled_entered,
        field.area_sampled_unit,
    )
    paddock_value, paddock_unit = area_form_initial(
        field.paddock_size_ha,
        field.paddock_size_entered,
        field.paddock_size_unit,
    )
    return {
        'area_sampled': area_value if area_value is not None else field.area_sampled_ha,
        'area_sampled_entered': field.area_sampled_entered,
        'area_sampled_unit': area_unit,
        'paddock_size': paddock_value if paddock_value is not None else field.paddock_size_ha,
        'paddock_size_entered': field.paddock_size_entered,
        'paddock_size_unit': paddock_unit,
    }


def grazing_form_initial(canonical_value, entered_value, unit_value, *, from_canonical):
    unit = unit_value or (DEFAULT_WEIGHT_UNIT if from_canonical == 'weight' else DEFAULT_TIME_UNIT)
    if entered_value is not None:
        return entered_value, unit
    if canonical_value is not None:
        from .measurement_units import from_days, from_kg

        if from_canonical == 'weight':
            return from_kg(canonical_value, unit), unit
        return from_days(canonical_value, unit), unit
    return None, unit
