from crispy_forms.layout import Column, Row

from ..constants import (
    AREA_UNIT_CHOICES,
    DEFAULT_AREA_UNIT,
    DEFAULT_DEPTH_UNIT,
    DEFAULT_TIME_UNIT,
    DEFAULT_WEIGHT_UNIT,
    DEPTH_UNIT_CHOICES,
    TIME_UNIT_CHOICES,
    WEIGHT_UNIT_CHOICES,
)


def unit_choice_field(label='Unit', initial=None, choices=None):
    from django import forms

    return forms.ChoiceField(
        choices=choices,
        required=True,
        label=label,
        initial=initial,
        widget=forms.Select(attrs={'class': 'form-select measurement-unit-select'}),
    )


def area_unit_field(initial=DEFAULT_AREA_UNIT):
    return unit_choice_field(initial=initial, choices=AREA_UNIT_CHOICES)


def depth_unit_field(initial=DEFAULT_DEPTH_UNIT):
    return unit_choice_field(initial=initial, choices=DEPTH_UNIT_CHOICES)


def weight_unit_field(initial=DEFAULT_WEIGHT_UNIT):
    return unit_choice_field(initial=initial, choices=WEIGHT_UNIT_CHOICES)


def time_unit_field(initial=DEFAULT_TIME_UNIT):
    return unit_choice_field(initial=initial, choices=TIME_UNIT_CHOICES)


def value_with_unit_row(value_field, unit_field, value_cols='col-md-8', unit_cols='col-md-4'):
    return Row(
        Column(value_field, css_class=value_cols),
        Column(unit_field, css_class=unit_cols),
        css_class='measurement-with-unit-row',
    )
