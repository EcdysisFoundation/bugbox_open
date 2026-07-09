from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from .constants import (
    AREA_UNIT_ACRES,
    AREA_UNIT_HECTARES,
    CANONICAL_AREA_UNIT,
    CANONICAL_DEPTH_UNIT,
    CANONICAL_WEIGHT_UNIT,
    DEPTH_UNIT_CM,
    DEPTH_UNIT_INCHES,
    TIME_UNIT_DAYS,
    TIME_UNIT_WEEKS,
    WEIGHT_UNIT_KG,
    WEIGHT_UNIT_LBS,
)

HECTARES_PER_ACRE = Decimal('0.40468564224')
CM_PER_INCH = Decimal('2.54')
KG_PER_LB = Decimal('0.45359237')
DAYS_PER_WEEK = 7


def _to_decimal(value):
    if value is None or value == '':
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None


def _quantize(value, places=2):
    if value is None:
        return None
    quantizer = Decimal('1').scaleb(-places)
    return value.quantize(quantizer, rounding=ROUND_HALF_UP)


def to_hectares(value, unit):
    amount = _to_decimal(value)
    if amount is None:
        return None
    if unit == AREA_UNIT_ACRES:
        return _quantize(amount * HECTARES_PER_ACRE)
    return _quantize(amount)


def from_hectares(value, unit=AREA_UNIT_HECTARES):
    amount = _to_decimal(value)
    if amount is None:
        return None
    if unit == AREA_UNIT_ACRES:
        return _quantize(amount / HECTARES_PER_ACRE)
    return _quantize(amount)


def to_cm(value, unit):
    amount = _to_decimal(value)
    if amount is None:
        return None
    if unit == DEPTH_UNIT_INCHES:
        return _quantize(amount * CM_PER_INCH)
    return _quantize(amount)


def from_cm(value, unit=DEPTH_UNIT_CM):
    amount = _to_decimal(value)
    if amount is None:
        return None
    if unit == DEPTH_UNIT_INCHES:
        return _quantize(amount / CM_PER_INCH)
    return _quantize(amount)


def to_kg(value, unit):
    amount = _to_decimal(value)
    if amount is None:
        return None
    if unit == WEIGHT_UNIT_LBS:
        return _quantize(amount * KG_PER_LB)
    return _quantize(amount)


def from_kg(value, unit=WEIGHT_UNIT_KG):
    amount = _to_decimal(value)
    if amount is None:
        return None
    if unit == WEIGHT_UNIT_LBS:
        return _quantize(amount / KG_PER_LB, places=0)
    return _quantize(amount)


def to_acres(value, unit):
    """Convert entered area to acres (legacy helper)."""
    amount = _to_decimal(value)
    if amount is None:
        return None
    if unit == AREA_UNIT_HECTARES:
        return _quantize(amount / HECTARES_PER_ACRE)
    return _quantize(amount)


def from_acres(value, unit=AREA_UNIT_ACRES):
    amount = _to_decimal(value)
    if amount is None:
        return None
    if unit == AREA_UNIT_HECTARES:
        return _quantize(amount * HECTARES_PER_ACRE)
    return _quantize(amount)


def to_inches(value, unit):
    amount = _to_decimal(value)
    if amount is None:
        return None
    if unit == DEPTH_UNIT_CM:
        return _quantize(amount / CM_PER_INCH)
    return _quantize(amount)


def from_inches(value, unit=DEPTH_UNIT_INCHES):
    amount = _to_decimal(value)
    if amount is None:
        return None
    if unit == DEPTH_UNIT_CM:
        return _quantize(amount * CM_PER_INCH)
    return _quantize(amount)


def to_pounds(value, unit):
    amount = _to_decimal(value)
    if amount is None:
        return None
    if unit == WEIGHT_UNIT_KG:
        return int((_quantize(amount / KG_PER_LB, places=4) or Decimal('0')).to_integral_value(rounding=ROUND_HALF_UP))
    return int(amount.to_integral_value(rounding=ROUND_HALF_UP))


def from_pounds(value, unit=WEIGHT_UNIT_LBS):
    amount = _to_decimal(value)
    if amount is None:
        return None
    if unit == WEIGHT_UNIT_KG:
        return _quantize(amount * KG_PER_LB)
    return _quantize(amount, places=0)


def to_days(value, unit):
    amount = _to_decimal(value)
    if amount is None:
        return None
    if unit == TIME_UNIT_WEEKS:
        return int((amount * DAYS_PER_WEEK).to_integral_value(rounding=ROUND_HALF_UP))
    return int(amount.to_integral_value(rounding=ROUND_HALF_UP))


def from_days(value, unit=TIME_UNIT_DAYS):
    amount = _to_decimal(value)
    if amount is None:
        return None
    if unit == TIME_UNIT_WEEKS:
        return _quantize(amount / DAYS_PER_WEEK)
    return _quantize(amount, places=0)


def format_area_hectares(value):
    amount = _to_decimal(value)
    if amount is None:
        return ''
    return f'{_quantize(amount)} hectares'


def format_weight_kg(value):
    amount = _to_decimal(value)
    if amount is None:
        return ''
    return f'{_quantize(amount)} kg'


def format_days(value):
    amount = _to_decimal(value)
    if amount is None:
        return ''
    return f'{int(amount.to_integral_value(rounding=ROUND_HALF_UP))} days'


def format_depth_cm(value):
    amount = _to_decimal(value)
    if amount is None:
        return ''
    return f'{_quantize(amount)} cm'


def parse_stored_numeric(value):
    if value is None or value == '':
        return None
    if isinstance(value, (int, float, Decimal)):
        return _to_decimal(value)
    text = str(value).strip()
    if not text:
        return None
    try:
        return _to_decimal(text)
    except (InvalidOperation, TypeError, ValueError):
        return None


AREA_UNIT_LABELS = {
    AREA_UNIT_ACRES: 'acres',
    AREA_UNIT_HECTARES: 'hectares',
}
DEPTH_UNIT_LABELS = {
    DEPTH_UNIT_INCHES: 'in',
    DEPTH_UNIT_CM: 'cm',
}
WEIGHT_UNIT_LABELS = {
    WEIGHT_UNIT_LBS: 'lbs',
    WEIGHT_UNIT_KG: 'kg',
}
TIME_UNIT_LABELS = {
    TIME_UNIT_DAYS: 'days',
    TIME_UNIT_WEEKS: 'weeks',
}


def format_entered_area(value, unit=AREA_UNIT_ACRES):
    amount = _to_decimal(value)
    if amount is None:
        return ''
    label = AREA_UNIT_LABELS.get(unit, unit)
    return f'{_quantize(amount)} {label}'


def format_entered_depth(value, unit=DEPTH_UNIT_INCHES):
    amount = _to_decimal(value)
    if amount is None:
        return ''
    label = DEPTH_UNIT_LABELS.get(unit, unit)
    return f'{_quantize(amount)} {label}'


def format_entered_weight(value, unit=WEIGHT_UNIT_LBS):
    amount = _to_decimal(value)
    if amount is None:
        return ''
    label = WEIGHT_UNIT_LABELS.get(unit, unit)
    if unit == WEIGHT_UNIT_KG:
        return f'{_quantize(amount)} {label}'
    return f'{int(amount.to_integral_value(rounding=ROUND_HALF_UP))} {label}'


def format_entered_duration(value, unit=TIME_UNIT_DAYS):
    amount = _to_decimal(value)
    if amount is None:
        return ''
    label = TIME_UNIT_LABELS.get(unit, unit)
    if unit == TIME_UNIT_WEEKS:
        return f'{_quantize(amount)} {label}'
    return f'{int(amount.to_integral_value(rounding=ROUND_HALF_UP))} {label}'


def canonical_matches_entered(entered, unit, canonical, *, measurement_type, tolerance=Decimal('0.02')):
    """Return True when canonical value matches convert(entered, unit) within tolerance."""
    if entered is None or canonical is None:
        return entered is None and canonical is None
    converters = {
        'area': to_hectares,
        'depth': to_cm,
        'weight': to_kg,
        'duration': to_days,
    }
    converter = converters.get(measurement_type)
    if converter is None:
        return False
    expected = converter(entered, unit)
    if expected is None:
        return False
    if measurement_type == 'duration':
        return int(expected) == int(canonical)
    return abs(_to_decimal(canonical) - expected) <= tolerance
