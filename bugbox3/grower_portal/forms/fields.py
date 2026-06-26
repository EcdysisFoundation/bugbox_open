from django import forms

from ..constants import PHONE_MAX_LENGTH
from ..phone import is_empty_phone, normalize_phone_number


class InternationalPhoneWidget(forms.TextInput):
    template_name = 'grower_portal/widgets/international_phone.html'

    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'form-control international-phone-input',
            'type': 'tel',
            'autocomplete': 'tel',
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)


class InternationalPhoneField(forms.CharField):
    widget = InternationalPhoneWidget

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', PHONE_MAX_LENGTH)
        kwargs.setdefault('required', False)
        super().__init__(*args, **kwargs)

    def to_python(self, value):
        if is_empty_phone(value):
            return ''
        return super().to_python(value)

    def validate(self, value):
        if is_empty_phone(value):
            return
        super().validate(value)

    def clean(self, value):
        value = super().clean(value)
        if is_empty_phone(value):
            return ''
        return normalize_phone_number(value)
