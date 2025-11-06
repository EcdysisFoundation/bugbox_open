from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Div, Row, Column, Field

from bugbox3.core.forms import ModelFormMixin
from ...models import TransectCode, CSVImportLog, GrowerApplication, GrowerProfile, Farm, Field
from ...constants import FIELD_TYPE_CHOICES

User = get_user_model()


class TransectCodeGenerationForm(forms.Form):
    count = forms.IntegerField(
        min_value=1,
        max_value=1000,
        label='Number of Codes to Generate',
        help_text='Enter a number between 1 and 1000. Codes are generated sequentially.'
    )
    prefix = forms.CharField(
        max_length=20,
        required=False,
        label='Code Prefix (Optional)',
        help_text='Optional prefix (e.g., "PLOT-A" → PLOT-A-00001). Numeric codes only, 5-digit minimum, auto-scales to 6+ digits.'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('count', css_class='form-group col-md-6 mb-3'),
                Column('prefix', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            Submit('submit', 'Generate Codes', css_class='btn btn-primary')
        )

    def clean_prefix(self):
        prefix = self.cleaned_data.get('prefix', '').strip()
        if prefix and not prefix.replace('-', '').replace('_', '').isalnum():
            raise ValidationError('Prefix must contain only alphanumeric characters, hyphens, or underscores')
        return prefix


class CSVUploadForm(forms.Form):
    csv_file = forms.FileField(
        label='CSV File',
        help_text='Select a CSV file to upload (max 10MB)',
        widget=forms.FileInput(attrs={'accept': '.csv'})
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 4}),
        label='Description/Annotations',
        help_text='Optional notes about this import',
        max_length=500
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.layout = Layout(
            'csv_file',
            'description',
            Submit('submit', 'Upload CSV', css_class='btn btn-primary')
        )

    def clean_csv_file(self):
        csv_file = self.cleaned_data.get('csv_file')
        if csv_file:
            if not csv_file.name.endswith('.csv'):
                raise ValidationError('File must be a CSV file (.csv extension)')
            if csv_file.size > 10 * 1024 * 1024:
                raise ValidationError('File size must not exceed 10MB')
        return csv_file


class ApplicationFilterForm(forms.Form):
    search = forms.CharField(
        required=False,
        label='Search',
        widget=forms.TextInput(attrs={
            'placeholder': 'Search by submission code, transect code, or grower name'
        })
    )
    status = forms.ChoiceField(
        required=False,
        label='Status',
        choices=[
            ('', 'All Statuses'),
            ('draft', 'Draft'),
            ('submitted', 'Submitted')
        ]
    )
    field_type = forms.ChoiceField(
        required=False,
        label='Field Type',
        choices=[('', 'All Types')] + list(FIELD_TYPE_CHOICES)
    )
    date_from = forms.DateField(
        required=False,
        label='Date From',
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    date_to = forms.DateField(
        required=False,
        label='Date To',
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.form_class = 'form-inline'
        self.helper.layout = Layout(
            Row(
                Column('search', css_class='form-group col-md-4 mb-2'),
                Column('status', css_class='form-group col-md-2 mb-2'),
                Column('field_type', css_class='form-group col-md-2 mb-2'),
                Column('date_from', css_class='form-group col-md-2 mb-2'),
                Column('date_to', css_class='form-group col-md-2 mb-2'),
                css_class='form-row'
            ),
            Submit('filter', 'Apply Filters', css_class='btn btn-primary btn-sm')
        )


class TransectCodeFilterForm(forms.Form):
    search = forms.CharField(
        required=False,
        label='Search Code',
        widget=forms.TextInput(attrs={'placeholder': 'Search by code or prefix'})
    )
    status = forms.ChoiceField(
        required=False,
        label='Status',
        choices=[
            ('', 'All'),
            ('active', 'Active'),
            ('inactive', 'Inactive')
        ]
    )
    usage = forms.ChoiceField(
        required=False,
        label='Usage',
        choices=[
            ('', 'All'),
            ('used', 'Used'),
            ('unused', 'Unused')
        ]
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.form_class = 'form-inline'
        self.helper.layout = Layout(
            Row(
                Column('search', css_class='form-group col-md-6 mb-2'),
                Column('status', css_class='form-group col-md-3 mb-2'),
                Column('usage', css_class='form-group col-md-3 mb-2'),
                css_class='form-row'
            ),
            Submit('filter', 'Apply Filters', css_class='btn btn-primary btn-sm')
        )


class GrowerFilterForm(forms.Form):
    search = forms.CharField(
        required=False,
        label='Search',
        widget=forms.TextInput(attrs={'placeholder': 'Search by name or email'})
    )
    profile_completed = forms.ChoiceField(
        required=False,
        label='Profile Status',
        choices=[
            ('', 'All'),
            ('completed', 'Completed'),
            ('incomplete', 'Incomplete')
        ]
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.form_class = 'form-inline'
        self.helper.layout = Layout(
            Row(
                Column('search', css_class='form-group col-md-8 mb-2'),
                Column('profile_completed', css_class='form-group col-md-4 mb-2'),
                css_class='form-row'
            ),
            Submit('filter', 'Apply Filters', css_class='btn btn-primary btn-sm')
        )


class FarmFilterForm(forms.Form):
    search = forms.CharField(
        required=False,
        label='Search',
        widget=forms.TextInput(attrs={'placeholder': 'Search by farm name'})
    )
    grower = forms.ModelChoiceField(
        required=False,
        queryset=User.objects.filter(groups__name='is_grower').distinct(),
        label='Grower',
        empty_label='All Growers'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.form_class = 'form-inline'
        self.helper.layout = Layout(
            Row(
                Column('search', css_class='form-group col-md-8 mb-2'),
                Column('grower', css_class='form-group col-md-4 mb-2'),
                css_class='form-row'
            ),
            Submit('filter', 'Apply Filters', css_class='btn btn-primary btn-sm')
        )


class FieldFilterForm(forms.Form):
    search = forms.CharField(
        required=False,
        label='Search',
        widget=forms.TextInput(attrs={'placeholder': 'Search by field name'})
    )
    field_type = forms.ChoiceField(
        required=False,
        label='Field Type',
        choices=[('', 'All Types')] + list(FIELD_TYPE_CHOICES)
    )
    grower = forms.ModelChoiceField(
        required=False,
        queryset=User.objects.filter(groups__name='is_grower').distinct(),
        label='Grower',
        empty_label='All Growers'
    )
    farm = forms.ModelChoiceField(
        required=False,
        queryset=Farm.objects.all(),
        label='Farm',
        empty_label='All Farms'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.form_class = 'form-inline'
        self.helper.layout = Layout(
            Row(
                Column('search', css_class='form-group col-md-4 mb-2'),
                Column('field_type', css_class='form-group col-md-3 mb-2'),
                Column('grower', css_class='form-group col-md-3 mb-2'),
                Column('farm', css_class='form-group col-md-2 mb-2'),
                css_class='form-row'
            ),
            Submit('filter', 'Apply Filters', css_class='btn btn-primary btn-sm')
        )

