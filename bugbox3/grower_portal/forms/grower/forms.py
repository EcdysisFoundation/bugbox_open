from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from crispy_forms.layout import Fieldset, Row, Column, HTML, Div, Submit
from bugbox3.core.forms import ModelFormMixin, Html5DateInput
from ...models import (
    GrowerProfile, Field, TransectCode, GrowerApplication,
    ManagementPractices, ApplicationMeasurement, GrazingEvent
)
from ...constants import (
    GENDER_CHOICES, RACE_CHOICES, FIELD_TYPE_CHOICES,
    TRANSITIONAL_STATUS_CHOICES, INSECTICIDE_FREQUENCY_CHOICES,
    PHONE_MAX_LENGTH, FARM_NAME_MAX_LENGTH, FIELD_NAME_MAX_LENGTH,
    CROP_VARIETY_MAX_LENGTH, FORAGE_VARIETIES_MAX_LENGTH,
    PADDOCK_SIZE_MAX_LENGTH, ROOTSTOCK_SPECIES_MAX_LENGTH,
    TRANSECT_CODE_MAX_LENGTH, AGE_MIN, AGE_MAX,
    LATITUDE_MIN, LATITUDE_MAX, LONGITUDE_MIN, LONGITUDE_MAX,
    CLASS_OF_ANIMAL_EXAMPLES
)

User = get_user_model()


class GrowerProfileCompletionForm(forms.ModelForm):
    """
    Form for completing grower profile information during initial signup.
    This form is shown only once after grower registration.
    """
    phone = forms.CharField(
        max_length=PHONE_MAX_LENGTH,
        required=False,
        label='Phone Number'
    )
    gender = forms.ChoiceField(
        choices=[('', 'Select Gender')] + GENDER_CHOICES,
        required=False,
        label='Gender'
    )
    age = forms.IntegerField(
        required=False,
        label='Age',
        help_text='Enter your age in years',
        min_value=AGE_MIN,
        max_value=AGE_MAX
    )
    race = forms.ChoiceField(
        choices=[('', 'Select Race')] + RACE_CHOICES,
        required=False,
        label='Race'
    )
    
    class Meta:
        model = GrowerProfile
        fields = ['phone', 'gender', 'age', 'race']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class ApplicationCreationForm(ModelFormMixin):
    farm_name = forms.CharField(
        max_length=FARM_NAME_MAX_LENGTH,
        label='Farm Name'
    )
    field_name = forms.CharField(
        max_length=FIELD_NAME_MAX_LENGTH,
        label='Field Name'
    )
    field_type = forms.ChoiceField(
        choices=FIELD_TYPE_CHOICES,
        label='Field Type'
    )
    latitude = forms.DecimalField(
        max_digits=9,
        decimal_places=6,
        required=False,
        min_value=LATITUDE_MIN,
        max_value=LATITUDE_MAX,
        label='Latitude',
        help_text='Field latitude (-90 to 90)'
    )
    longitude = forms.DecimalField(
        max_digits=9,
        decimal_places=6,
        required=False,
        min_value=LONGITUDE_MIN,
        max_value=LONGITUDE_MAX,
        label='Longitude',
        help_text='Field longitude (-180 to 180)'
    )
    crop_variety = forms.CharField(
        max_length=CROP_VARIETY_MAX_LENGTH,
        required=False,
        label='Crop Variety',
        help_text='For crop fields and orchards'
    )
    forage_varieties = forms.CharField(
        max_length=FORAGE_VARIETIES_MAX_LENGTH,
        required=False,
        label='Forage Varieties',
        help_text='For rangeland'
    )
    paddock_size = forms.CharField(
        max_length=PADDOCK_SIZE_MAX_LENGTH,
        required=False,
        label='Paddock Size',
        help_text='For rangeland'
    )
    rootstock_species = forms.CharField(
        max_length=ROOTSTOCK_SPECIES_MAX_LENGTH,
        required=False,
        label='Rootstock Species',
        help_text='For orchards'
    )
    transitional_status = forms.ChoiceField(
        choices=[('', '---')] + TRANSITIONAL_STATUS_CHOICES,
        required=False,
        label='Transitional Status',
        help_text='For orchards'
    )
    date_sampled = forms.DateField(
        widget=Html5DateInput(),
        label='Date Sampled',
        help_text='Date when samples were collected'
    )
    transect_code_1 = forms.CharField(
        max_length=TRANSECT_CODE_MAX_LENGTH,
        label='Transect Code 1'
    )
    transect_code_2 = forms.CharField(
        max_length=TRANSECT_CODE_MAX_LENGTH,
        required=False,
        label='Transect Code 2'
    )
    transect_code_3 = forms.CharField(
        max_length=TRANSECT_CODE_MAX_LENGTH,
        required=False,
        label='Transect Code 3'
    )
    transect_code_4 = forms.CharField(
        max_length=TRANSECT_CODE_MAX_LENGTH,
        required=False,
        label='Transect Code 4'
    )
    
    class Meta:
        model = GrowerApplication
        fields = ['date_sampled', 'transect_code_1', 'transect_code_2', 'transect_code_3', 'transect_code_4']
    
    required_fields = ['farm_name', 'field_name', 'field_type', 'date_sampled', 'transect_code_1']
    
    def get_primary_layout(self):
        return [
            Fieldset(
                'Farm Information',
                Row(Column('farm_name'))
            ),
            Fieldset(
                'Field Information',
                Row(Column('field_name')),
                Row(Column('field_type')),
                Div(
                    Row(
                        Column('latitude', css_class='col-md-6'),
                        Column('longitude', css_class='col-md-6')
                    ),
                    css_class='gps-coordinates'
                ),
                Div(
                    css_id='field_specific_properties',
                    css_class='mt-3'
                ),
                Div(
                    HTML('<h6>Crop Information</h6>'),
                    Row(Column('crop_variety')),
                    css_id='crop_variety_field',
                    css_class='field-specific',
                    style='display:none;'
                ),
                Div(
                    HTML('<h6>Rangeland Information</h6>'),
                    Row(Column('forage_varieties')),
                    Row(Column('paddock_size')),
                    css_id='rangeland_fields',
                    css_class='field-specific',
                    style='display:none;'
                ),
                Div(
                    HTML('<h6>Orchard Information</h6>'),
                    Row(Column('rootstock_species')),
                    Row(Column('transitional_status')),
                    css_id='orchard_specific_fields',
                    css_class='field-specific',
                    style='display:none;'
                )
            ),
            Fieldset(
                'Application Details',
                Row(Column('date_sampled'))
            ),
            Fieldset(
                'Transect Codes',
                HTML('<p class="text-muted">Enter 1-4 transect codes. At least one code is required.</p>'),
                Row(
                    Column('transect_code_1', css_class='col-md-6'),
                    Column('transect_code_2', css_class='col-md-6')
                ),
                Row(
                    Column('transect_code_3', css_class='col-md-6'),
                    Column('transect_code_4', css_class='col-md-6')
                )
            ),
            Submit('submit', 'Create Application', css_class='btn btn-primary btn-lg')
        ]
    
    def clean(self):
        cleaned_data = super().clean()
        
        transect_codes = []
        for i in range(1, 5):
            code = cleaned_data.get(f'transect_code_{i}')
            if code:
                code = code.strip()
                transect_codes.append(code)
                
                if not TransectCode.objects.filter(transect_code=code, is_active=True).exists():
                    raise ValidationError(f'Transect code "{code}" does not exist or is not active.')
                
                if GrowerApplication.objects.filter(**{f'transect_code_{i}': code, 'is_submitted': True}).exists():
                    raise ValidationError(f'Transect code "{code}" has already been used in a submitted application.')
        
        if not transect_codes:
            raise ValidationError('At least one transect code is required.')
        
        if len(transect_codes) != len(set(transect_codes)):
            raise ValidationError('Transect codes must be unique within the application.')
        
        field_type = cleaned_data.get('field_type')
        
        if field_type == 'crop':
            crop_variety = cleaned_data.get('crop_variety', '').strip()
            if not crop_variety:
                self.add_error('crop_variety', 'Crop variety is required for crop fields.')
        elif field_type == 'range':
            forage_varieties = cleaned_data.get('forage_varieties', '').strip()
            if not forage_varieties:
                self.add_error('forage_varieties', 'Forage varieties are required for rangeland.')
        elif field_type == 'orchard':
            rootstock_species = cleaned_data.get('rootstock_species', '').strip()
            if not rootstock_species:
                self.add_error('rootstock_species', 'Rootstock species is required for orchards.')
        
        return cleaned_data


class ManagementPracticesForm(ModelFormMixin):
    class Meta:
        model = ManagementPractices
        fields = [
            'uses_tillage', 'tillage_depth',
            'uses_cover_crop', 'cover_crop_termination',
            'uses_synthetic_fertilizers', 'uses_synthetic_insecticides',
            'uses_synthetic_herbicides', 'uses_synthetic_fungicides',
            'uses_organic_amendments', 'organic_amendment_types',
            'uses_grazing', 'grazer_types',
            'applies_insecticides_dewormers', 'insecticide_dewormer_frequency',
            'insecticide_dewormer_comments',
            'allows_ground_cover', 'ground_cover_management', 'tills_between_rows'
        ]
    
    required_fields = []
    
    def get_primary_layout(self):
        return [
            Fieldset(
                'Tillage Practices',
                Row(Column('uses_tillage')),
                Div(
                    Row(Column('tillage_depth')),
                    css_id='tillage_depth_field',
                    style='display:none;'
                )
            ),
            Fieldset(
                'Cover Crops',
                Row(Column('uses_cover_crop')),
                Div(
                    Row(Column('cover_crop_termination')),
                    css_id='cover_crop_fields',
                    style='display:none;'
                )
            ),
            Fieldset(
                'Synthetic Inputs',
                Row(
                    Column('uses_synthetic_fertilizers', css_class='col-md-6'),
                    Column('uses_synthetic_insecticides', css_class='col-md-6')
                ),
                Row(
                    Column('uses_synthetic_herbicides', css_class='col-md-6'),
                    Column('uses_synthetic_fungicides', css_class='col-md-6')
                )
            ),
            Fieldset(
                'Organic Amendments',
                Row(Column('uses_organic_amendments')),
                Div(
                    Row(Column('organic_amendment_types')),
                    HTML('<small class="form-text text-muted">e.g., Manure, Compost, Compost Tea, Organic Fertilizer, Other</small>'),
                    css_id='organic_amendment_fields',
                    style='display:none;'
                )
            ),
            Fieldset(
                'Grazing Practices',
                Row(Column('uses_grazing')),
                Div(
                    Row(Column('grazer_types')),
                    HTML('<small class="form-text text-muted">e.g., Chickens, Livestock, Other</small>'),
                    Row(Column('applies_insecticides_dewormers')),
                    Div(
                        Row(Column('insecticide_dewormer_frequency')),
                        Row(Column('insecticide_dewormer_comments')),
                        css_id='insecticide_fields',
                        style='display:none;'
                    ),
                    css_id='grazing_fields',
                    style='display:none;'
                )
            ),
            Fieldset(
                'Orchard-Specific Practices',
                Row(Column('allows_ground_cover')),
                Div(
                    Row(Column('ground_cover_management')),
                    css_id='ground_cover_fields',
                    style='display:none;'
                ),
                Row(Column('tills_between_rows')),
                css_id='orchard_practices',
                css_class='orchard-only'
            ),
            Submit('submit', 'Save and Continue', css_class='btn btn-primary')
        ]


class ApplicationMeasurementForm(ModelFormMixin):
    class Meta:
        model = ApplicationMeasurement
        fields = [
            'transect_latitude', 'transect_longitude',
            'acres_sampled', 'years_under_management',
            'supports_dairy', 'is_confined_dairy', 'comments'
        ]
    
    required_fields = ['acres_sampled', 'years_under_management']
    
    def get_primary_layout(self):
        return [
            Fieldset(
                'Sample Specifications',
                Row(
                    Column('acres_sampled', css_class='col-md-6'),
                    Column('years_under_management', css_class='col-md-6')
                )
            ),
            Fieldset(
                'Dairy Operation',
                Row(Column('supports_dairy')),
                Div(
                    Row(Column('is_confined_dairy')),
                    css_id='confined_dairy_field',
                    style='display:none;'
                )
            ),
            Fieldset(
                'Comments',
                Row(Column('comments'))
            )
        ]


class GrazingEventForm(ModelFormMixin):
    class Meta:
        model = GrazingEvent
        fields = [
            'class_of_animal', 'number_of_animals', 'average_weight_lbs',
            'duration_days', 'rest_period_days'
        ]
    
    required_fields = []
    
    def get_primary_layout(self):
        return [
            Fieldset(
                'Animal Information',
                Row(Column('class_of_animal')),
                HTML(f'<small class="form-text text-muted">{CLASS_OF_ANIMAL_EXAMPLES}</small>'),
                Row(
                    Column('number_of_animals', css_class='col-md-6'),
                    Column('average_weight_lbs', css_class='col-md-6')
                )
            ),
            Fieldset(
                'Grazing Schedule',
                Row(
                    Column('duration_days', css_class='col-md-6'),
                    Column('rest_period_days', css_class='col-md-6')
                )
            )
        ]