from django import template

from bugbox3.grower_portal.constants import (
    DEFAULT_DEPTH_UNIT,
    DEFAULT_TIME_UNIT,
    DEFAULT_WEIGHT_UNIT,
)
from bugbox3.grower_portal.measurement_units import (
    format_area_hectares,
    format_days,
    format_depth_cm,
    format_entered_area as fmt_entered_area,
    format_entered_depth as fmt_entered_depth,
    format_entered_duration as fmt_entered_duration,
    format_entered_weight as fmt_entered_weight,
    format_weight_kg,
    from_cm,
    from_days,
    from_hectares,
    from_kg,
    parse_stored_numeric,
)

register = template.Library()


@register.filter
def format_stored_area(value):
    return format_area_hectares(value)


@register.filter
def format_stored_paddock_size(value):
    hectares = parse_stored_numeric(value)
    if hectares is None:
        return value
    return format_area_hectares(hectares)


@register.filter
def format_stored_depth(value):
    cm = parse_stored_numeric(value)
    if cm is None:
        return value
    return format_depth_cm(cm)


@register.filter
def format_stored_weight(value, unit=DEFAULT_WEIGHT_UNIT):
    if unit and unit != DEFAULT_WEIGHT_UNIT:
        amount = from_kg(value, unit)
        if amount is None:
            return ''
        return fmt_entered_weight(amount, unit)
    return format_weight_kg(value)


@register.filter
def format_stored_duration(value, unit=DEFAULT_TIME_UNIT):
    if unit and unit != DEFAULT_TIME_UNIT:
        amount = from_days(value, unit)
        if amount is None:
            return ''
        return fmt_entered_duration(amount, unit)
    return format_days(value)


@register.filter
def format_entered_area(value, unit):
    return fmt_entered_area(value, unit)


@register.filter
def format_entered_depth(value, unit):
    return fmt_entered_depth(value, unit or DEFAULT_DEPTH_UNIT)


@register.filter
def format_entered_weight(value, unit):
    return fmt_entered_weight(value, unit or DEFAULT_WEIGHT_UNIT)


@register.filter
def format_entered_duration(value, unit):
    return fmt_entered_duration(value, unit or DEFAULT_TIME_UNIT)
