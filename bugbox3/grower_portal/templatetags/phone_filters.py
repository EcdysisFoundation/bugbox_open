from django import template

from ..phone import format_phone_for_display, is_empty_phone

register = template.Library()


@register.filter
def format_phone(value):
    return format_phone_for_display(value)


@register.filter
def has_phone(value):
    return not is_empty_phone(value)
