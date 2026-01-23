import pytz
from django import template
from django.utils.dateformat import format

from ..middleware import convert_to_user_timezone

register = template.Library()


@register.filter
def user_timezone(value, user_tz_string='UTC'):
    if not value:
        return value
    return convert_to_user_timezone(value, user_tz_string)


@register.filter
def user_date(value, user_tz_string='UTC'):
    if not value:
        return value

    try:
        _ = value.tzinfo
        dt = convert_to_user_timezone(value, user_tz_string)
        return format(dt, 'F d, Y')
    except AttributeError:
        return value.strftime('%B %d, %Y')


@register.filter
def user_datetime(value, user_tz_string='UTC'):
    if not value:
        return value

    dt = convert_to_user_timezone(value, user_tz_string)
    return format(dt, 'F d, Y g:i A')


@register.filter
def user_time(value, user_tz_string='UTC'):
    if not value:
        return value

    dt = convert_to_user_timezone(value, user_tz_string)
    return format(dt, 'g:i A')


@register.filter
def user_date_short(value, user_tz_string='UTC'):
    if not value:
        return value

    try:
        _ = value.tzinfo
        dt = convert_to_user_timezone(value, user_tz_string)
        return format(dt, 'M d, Y')
    except AttributeError:
        return value.strftime('%b %d, %Y')


@register.simple_tag
def timezone_name(user_tz_string='UTC'):
    try:
        tz = pytz.timezone(user_tz_string)
        return tz.zone
    except (pytz.exceptions.UnknownTimeZoneError, AttributeError):
        return 'UTC'
