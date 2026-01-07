from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Div, Row, Column, Field
import csv
import io

from bugbox3.core.forms import ModelFormMixin
from ...models import TransectCode, CSVImportLog, GrowerApplication, GrowerProfile, Farm, Field
from ...constants import FIELD_TYPE_CHOICES, CSV_IMPORT_SCHEMAS

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

    def _classify_and_get_missing_headers(self, headers):
        """
        Classify the CSV file into haney, plfa, or basic based on the headers, and return missing headers.
        """
        headers = set(headers)

        # Calculate how much the csv headers overlap with each schema's required headers
        candidates = {}
        for schema_key, schema_config in CSV_IMPORT_SCHEMAS.items():
            required_headers = set(schema_config['required_headers'])
            overlap_count = len(headers & required_headers)
            candidates[schema_key] = overlap_count

        # Get the schema with the highest overlap
        best_schema_key = max(candidates, key=candidates.get)
        schema_config = CSV_IMPORT_SCHEMAS[best_schema_key]
        required = set(schema_config['required_headers'])
        missing = required - headers

        return schema_config['name'], missing

    def clean_csv_file(self):
        csv_file = self.cleaned_data.get('csv_file')
        if csv_file:
            if not csv_file.name.endswith('.csv'):
                raise ValidationError('File must be a CSV file (.csv extension)')
            if csv_file.size > 10 * 1024 * 1024:
                raise ValidationError('File size must not exceed 10MB')

            # Read and validate CSV headers
            try:
                csv_file.seek(0)
                content = csv_file.read()
                if isinstance(content, bytes):
                    content = content.decode('utf-8-sig')

                csv_reader = csv.DictReader(io.StringIO(content))
                headers = csv_reader.fieldnames

                if not headers:
                    raise ValidationError(
                        'CSV file appears to be empty or has no headers'
                    )

                # Check for required fields
                headers_stripped = [h.strip() if h else '' for h in headers]
                schema, missing_headers = self._classify_and_get_missing_headers(headers_stripped)

                if missing_headers:
                    missing_list = ', '.join(missing_headers)
                    raise ValidationError(
                        f'{schema} CSV file is missing required columns: {missing_list}. '
                        f'Please ensure all required columns are present in the header row.'
                    )

            except csv.Error as e:
                raise ValidationError(f'Error reading CSV file: {str(e)}')
            except UnicodeDecodeError as _e:
                raise ValidationError(
                    'CSV file encoding error. Please ensure the file is UTF-8 encoded.'
                )
            except Exception as e:
                raise ValidationError(f'Error validating CSV file: {str(e)}')

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
    linked_status = forms.ChoiceField(
        required=False,
        label='Link Status',
        choices=[
            ('', 'All Applications'),
            ('linked', 'Linked to Account'),
            ('unlinked', 'Not Linked')
        ]
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.form_class = 'form-inline'
        self.helper.layout = Layout(
            Row(
                Column('search', css_class='form-group col-md-3 mb-2'),
                Column('status', css_class='form-group col-md-2 mb-2'),
                Column('field_type', css_class='form-group col-md-2 mb-2'),
                Column('linked_status', css_class='form-group col-md-2 mb-2'),
                Column('date_from', css_class='form-group col-md-1.5 mb-2'),
                Column('date_to', css_class='form-group col-md-1.5 mb-2'),
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
