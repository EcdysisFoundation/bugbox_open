from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Layout, Row, Submit
from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from ...constants import FIELD_TYPE_CHOICES, LABEL_PROJECT_CHOICES
from ...models import Farm

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
        help_text=(
            'Optional prefix (e.g., "PLOT-A" → PLOT-A-00001). '
            'Numeric codes only, 5-digit minimum, auto-scales to 6+ digits.'
        )
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


class GrowerSampleCodeLinkForm(forms.Form):
    """Link a grower account to a samplecode"""

    grower_email = forms.EmailField(
        label='Grower email',
        help_text='Email of the grower account (must be in the is_grower group).',
        widget=forms.EmailInput(attrs={'placeholder': 'grower@example.com'}),
    )
    site_code = forms.CharField(
        max_length=20,
        label='Site / sample code',
        help_text='Transect code (Avalanche) or site code (Ignite), e.g. 5001 or AVALANCHE-A-00001.',
        widget=forms.TextInput(attrs={'placeholder': '5001'}),
    )
    year_sampled = forms.IntegerField(
        min_value=2000,
        max_value=2100,
        label='Year sampled',
        help_text='Year used to scope CSV and bird results for this grower.',
    )
    project_type = forms.ChoiceField(
        choices=LABEL_PROJECT_CHOICES,
        label='Project',
        help_text='Must match how this code is used in lab data (Ignite vs Avalanche).',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('grower_email', css_class='form-group col-md-6 mb-3'),
                Column('site_code', css_class='form-group col-md-6 mb-3'),
                css_class='form-row',
            ),
            Row(
                Column('year_sampled', css_class='form-group col-md-6 mb-3'),
                Column('project_type', css_class='form-group col-md-6 mb-3'),
                css_class='form-row',
            ),
            Submit('submit', 'Link grower to code', css_class='btn btn-primary'),
        )

    def clean_grower_email(self):
        email = self.cleaned_data['grower_email'].strip().lower()
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise ValidationError('No user account found with this email.')
        if not user.groups.filter(name='is_grower').exists():
            raise ValidationError('This user is not in the grower group (is_grower).')
        self.cleaned_data['grower_user'] = user
        return email

    def clean_site_code(self):
        return self.cleaned_data['site_code'].strip()
