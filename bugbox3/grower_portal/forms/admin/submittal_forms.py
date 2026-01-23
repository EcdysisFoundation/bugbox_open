from django import forms
from django.core.exceptions import ValidationError

from ...constants import CLUSTER_NUMBER_MAX_LENGTH
from ...models import LabelGeneration


class SubmittalFormGenerationForm(forms.Form):
    """generate submittal forms based on cluster and year"""

    cluster_number = forms.CharField(
        max_length=CLUSTER_NUMBER_MAX_LENGTH,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., C1, C2',
            'id': 'id_cluster_number'
        }),
        label='Cluster Number',
        help_text='Enter the cluster number (e.g., C1, C2)'
    )

    year = forms.IntegerField(
        min_value=2020,
        max_value=2030,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 2024',
            'id': 'id_year'
        }),
        label='Year',
        help_text='Year for the submittal form'
    )

    generate_soil = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'id_generate_soil'
        }),
        label='Generate Soil Submittal Form',
        help_text='Generate submittal form for soil samples'
    )

    generate_plant = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'id_generate_plant'
        }),
        label='Generate Plant Submittal Form',
        help_text='Generate submittal form for plant samples (forage)'
    )

    def clean(self):
        """Validate that LabelGeneration exists for the cluster and year"""
        cleaned_data = super().clean()
        cluster = cleaned_data.get('cluster_number')
        year = cleaned_data.get('year')

        if cluster and year:
            if not LabelGeneration.objects.filter(
                cluster_number=cluster,
                year=year
            ).exists():
                raise ValidationError(
                    f'No labels found for cluster {cluster} in year {year}. '
                    'Please generate labels first using the Label Management page.'
                )

        return cleaned_data
