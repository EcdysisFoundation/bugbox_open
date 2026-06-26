"""Phone number validation"""
from django.core.exceptions import ValidationError

import phonenumbers
from phonenumbers import NumberParseException, PhoneNumberFormat

from .constants import PHONE_MAX_LENGTH

DEFAULT_PHONE_REGION = 'US'
EMPTY_PHONE_VALUES = frozenset({'', 'nan', 'n/a', 'na', 'none'})


def is_empty_phone(value):
    if value is None:
        return True
    return str(value).strip().lower() in EMPTY_PHONE_VALUES


def _parse_phone(value, default_region=DEFAULT_PHONE_REGION):
    value = str(value).strip()
    if value.startswith('+'):
        return phonenumbers.parse(value, None)
    return phonenumbers.parse(value, default_region)


def normalize_phone_number(value, default_region=DEFAULT_PHONE_REGION):
    """Validate and return an E.164 phone number, or '' when empty"""
    if is_empty_phone(value):
        return ''

    try:
        number = _parse_phone(value, default_region)
    except NumberParseException as exc:
        raise ValidationError('Enter a valid phone number with country code.') from exc

    if not phonenumbers.is_valid_number(number):
        raise ValidationError('Enter a valid phone number for the selected country.')

    e164 = phonenumbers.format_number(number, PhoneNumberFormat.E164)
    if len(e164) > PHONE_MAX_LENGTH:
        raise ValidationError('Phone number is too long.')
    return e164


def try_normalize_phone_number(value, default_region=DEFAULT_PHONE_REGION):
    if is_empty_phone(value):
        return '', None

    try:
        number = _parse_phone(value, default_region)
    except NumberParseException as exc:
        return None, str(exc)

    if not phonenumbers.is_valid_number(number):
        return None, 'invalid number'

    e164 = phonenumbers.format_number(number, PhoneNumberFormat.E164)
    if len(e164) > PHONE_MAX_LENGTH:
        return None, 'number too long'
    return e164, None


def format_phone_for_display(value, default_region=DEFAULT_PHONE_REGION):
    if is_empty_phone(value):
        return ''

    try:
        number = _parse_phone(value, default_region)
        if phonenumbers.is_valid_number(number):
            return phonenumbers.format_number(number, PhoneNumberFormat.INTERNATIONAL)
    except NumberParseException:
        pass

    return str(value).strip()
