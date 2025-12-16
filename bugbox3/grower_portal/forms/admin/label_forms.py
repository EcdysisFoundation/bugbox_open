from django import forms
from django.core.exceptions import ValidationError
from ...constants import (
    LABEL_PROJECT_CHOICES, LABEL_CATEGORY_CHOICES,
    SAMPLE_TYPES,
    LABEL_COUNT_MIN, LABEL_COUNT_MAX, CLUSTER_NUMBER_MAX_LENGTH
)


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
        
        project_type = self.data.get('project_type') or self.initial.get('project_type')
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
        min_value=1,
        max_value=1000,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '40',
            'id': 'id_number_of_transects'
        }),
        label='Number of Transects',
        help_text='Total number of transect codes to generate'
    )

