from django import forms
from django.core.exceptions import ValidationError

from ...constants import (
    CLUSTER_NUMBER_MAX_LENGTH,
    IGNITE_INNER_SAMPLE_TYPES,
    IGNITE_OUTER_ONLY_SAMPLE_TYPE_LABELS,
    IGNITE_OUTER_SAMPLE_TYPES,
    LABEL_CATEGORY_CHOICES,
    LABEL_COUNT_MAX,
    LABEL_COUNT_MIN,
    LABEL_PROJECT_CHOICES,
    SAMPLE_TYPES,
)
from ...models import LabelGeneration


class LabelGenerationForm(forms.Form):
    project_type = forms.ChoiceField(
        choices=LABEL_PROJECT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_project_type'}),
        label='Project Type'
    )

    label_category = forms.ChoiceField(
        choices=LABEL_CATEGORY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_label_category'}),
        label='Label Category'
    )

    cluster_number = forms.CharField(
        max_length=CLUSTER_NUMBER_MAX_LENGTH,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., C1, C2',
            'id': 'id_cluster_number'
        }),
        label='Cluster Number',
        help_text='Enter cluster identifier (e.g., C1, C2)'
    )

    year = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '2025',
            'id': 'id_year'
        }),
        label='Year',
        min_value=2020,
        max_value=2100
    )

    labels_per_type = forms.IntegerField(
        min_value=LABEL_COUNT_MIN,
        max_value=LABEL_COUNT_MAX,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'id': 'id_labels_per_type'
        }),
        label='Labels per Sample Type',
        help_text=f'Number of labels to generate for each selected sample type ({LABEL_COUNT_MIN}-{LABEL_COUNT_MAX})'
    )

    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Optional notes or description'
        }),
        label='Description (Optional)'
    )

    sample_types = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Sample Types'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.data.get('project_type') or self.initial.get('project_type')
        self.fields['sample_types'].choices = SAMPLE_TYPES

    def clean(self):
        cleaned_data = super().clean()
        label_category = cleaned_data.get('label_category')
        sample_types = cleaned_data.get('sample_types')

        if label_category == 'inner':
            if not sample_types:
                raise ValidationError('Please select at least one sample type for inner labels.')

        return cleaned_data


class QuickLabelGenerationForm(forms.Form):
    """Quick form for generating all labels for a field trip"""

    project_type = forms.ChoiceField(
        choices=LABEL_PROJECT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_quick_project_type'}),
        label='Project Type'
    )

    label_category = forms.ChoiceField(
        choices=LABEL_CATEGORY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_quick_label_category'}),
        label='Label Category',
        initial='inner'
    )

    cluster_number = forms.CharField(
        max_length=CLUSTER_NUMBER_MAX_LENGTH,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., C1, C2',
            'id': 'id_quick_cluster_number'
        }),
        label='Cluster Number',
        help_text='Enter cluster identifier (e.g., C1, C2)'
    )

    year = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '2025',
            'id': 'id_quick_year'
        }),
        label='Year',
        min_value=2020,
        max_value=2100
    )

    number_of_transects = forms.IntegerField(
        required=False,
        min_value=1,
        max_value=1000,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '40',
            'id': 'id_number_of_transects'
        }),
        label='Number of Transects/Sites',
        help_text=(
            'For Avalanche: number of transect codes. '
            'For Ignite: number of sites (each site has 4 transects T1-T4)'
        )
    )

    inner_label_generation = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_inner_label_generation'
        }),
        label='Select Inner Label Generation',
        help_text='Choose the inner label generation to use for outer labels'
    )

    excluded_sample_types = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input',
            'id': 'id_excluded_sample_types'
        }),
        label='Exclude Sample Types',
        help_text='Select sample types to exclude from label generation'
    )

    include_forage_labels = forms.BooleanField(
        required=False,
        initial=False,
        label='Include Forage labels',
        help_text='Adds Forage inner labels (T1-T4 per site). Shown for Ignite inner quick generate only.',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'id_include_forage_labels'}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        cluster = self.data.get('cluster_number') if self.data else None
        year = self.data.get('year') if self.data else None
        project_type = self.data.get('project_type') if self.data else None
        label_category = self.data.get('label_category') if self.data else 'inner'

        choices = [('', '-- Enter cluster and year to see options --')]

        if cluster and year:
            try:
                year_int = int(year)
                filter_kwargs = {
                    'label_category': 'inner',
                    'cluster_number': cluster,
                    'year': year_int
                }
                if project_type:
                    filter_kwargs['project_type'] = project_type

                inner_generations = LabelGeneration.objects.filter(**filter_kwargs).order_by('-generated_at')[:50]

                for gen in inner_generations:
                    if (gen.generation_params or {}).get('ignite_forage_supplement'):
                        continue
                    transect_count = len(gen.transect_codes_generated) if gen.transect_codes_generated else 0
                    project_label = dict(LABEL_PROJECT_CHOICES).get(gen.project_type, gen.project_type)
                    label = f"[{project_label}] Generated on {gen.generated_at.strftime(
                        '%Y-%m-%d %H:%M')} - {gen.total_labels_generated} labels - {transect_count} sites/transects"
                    choices.append((str(gen.id), label))
            except (ValueError, TypeError):
                pass

        self.fields['inner_label_generation'].choices = choices

        if project_type == 'ignite':
            if label_category == 'outer':
                available_types = IGNITE_OUTER_SAMPLE_TYPES
            else:
                available_types = IGNITE_INNER_SAMPLE_TYPES
        else:
            available_types = [code for code, _ in SAMPLE_TYPES]

        type_choices = [
            (
                code,
                IGNITE_OUTER_ONLY_SAMPLE_TYPE_LABELS.get(code, dict(SAMPLE_TYPES).get(code, code)),
            )
            for code in available_types
        ]
        self.fields['excluded_sample_types'].choices = type_choices

    def clean(self):
        cleaned_data = super().clean()
        label_category = cleaned_data.get('label_category')
        number_of_transects = cleaned_data.get('number_of_transects')
        inner_label_generation = cleaned_data.get('inner_label_generation')

        if label_category == 'outer':
            if not inner_label_generation:
                raise ValidationError('Please select an inner label generation for outer labels.')
        elif label_category == 'inner':
            if not number_of_transects:
                raise ValidationError('Number of transects is required for inner labels.')

        return cleaned_data
