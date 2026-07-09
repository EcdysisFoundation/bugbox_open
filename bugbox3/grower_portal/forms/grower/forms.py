from datetime import date

from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Column, Div, Fieldset, Layout, Row, Submit
from django import forms
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.forms import inlineformset_factory

from bugbox3.core.forms import Html5DateInput, ModelFormMixin

from ...forms.fields import InternationalPhoneField
from ...constants import (
    ADDRESS_LINE_MAX_LENGTH,
    AGE_MAX,
    AGE_MIN,
    AREA_SAMPLED_HA_MAX,
    AREA_SAMPLED_HA_MIN,
    AREA_UNIT_ACRES,
    AVERAGE_WEIGHT_KG_MAX,
    AVERAGE_WEIGHT_KG_MIN,
    COVER_CROP_TERMINATION_CHOICES,
    CROP_SUBTYPE_CHOICES,
    CROP_TYPE_CHOICES,
    CROP_VARIETIES_MAX_LENGTH,
    DEFAULT_AREA_UNIT,
    DEFAULT_DEPTH_UNIT,
    DEFAULT_TIME_UNIT,
    DEFAULT_WEIGHT_UNIT,
    DEPTH_UNIT_INCHES,
    DURATION_DAYS_MAX,
    DURATION_DAYS_MIN,
    FARM_NAME_MAX_LENGTH,
    FIELD_NAME_MAX_LENGTH,
    FIELD_TYPE_CHOICES,
    FORAGE_VARIETIES_MAX_LENGTH,
    GENDER_CHOICES,
    GRAZER_TYPES_CHOICES,
    GROUND_COVER_MANAGEMENT_CHOICES,
    LABEL_PROJECT_CHOICES,
    MAX_ANIMAL_ENTRIES_PER_GRAZING_EVENT,
    ORCHARD_CROP_TYPE_CHOICES,
    ORGANIC_AMENDMENT_CHOICES,
    PADDOCK_SIZE_MAX_LENGTH,
    PHONE_MAX_LENGTH,
    POSTAL_CODE_MAX_LENGTH,
    RACE_ANOTHER_BACKGROUND,
    RACE_CHOICES,
    RACE_INDIGENOUS,
    RACE_OTHER_MAX_LENGTH,
    REST_PERIOD_DAYS_MAX,
    REST_PERIOD_DAYS_MIN,
    RESULT_TYPE_CHOICES,
    ROOTSTOCK_SPECIES_MAX_LENGTH,
    TILLAGE_DEPTH_MAX_LENGTH,
    TILLAGE_METHODS_MAX_LENGTH,
    TIME_UNIT_DAYS,
    TRANSITIONAL_STATUS_CHOICES,
    WEIGHT_UNIT_LBS,
    YEARS_UNDER_MANAGEMENT_MAX,
    YEARS_UNDER_MANAGEMENT_MIN,
)
from ...measurement_capture import (
    area_form_initial,
    capture_area_measurement,
    capture_depth_measurement,
    capture_duration_measurement,
    capture_weight_measurement,
    depth_form_initial,
    grazing_form_initial,
)
from ..measurement_fields import area_unit_field, depth_unit_field, time_unit_field, value_with_unit_row, weight_unit_field
from ...country_choices import COUNTRY_CHOICES
from ...address import validate_grower_address
from ...models import (
    DropPlateReading,
    GrazingEvent,
    GrazingEventAnimal,
    GrowerApplication,
    GrowerProfile,
    InfiltrationRingReading,
    InfiltrometerReading,
    ManagementPractices,
    SampleCode,
    SoilCompactionReading,
    SoilReading,
    TransectMeasurement,
    VegetationReading,
)

User = get_user_model()


class GrowerProfileCompletionForm(forms.ModelForm):
    """
    Form for completing grower profile information during initial signup.
    """
    phone = InternationalPhoneField(
        label='Phone Number',
        help_text='Select your country and enter your phone number.',
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
        choices=[('', 'Select racial or ethnic background')] + RACE_CHOICES,
        required=False,
        label='Racial or ethnic background',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    race_indigenous_country = forms.ChoiceField(
        choices=COUNTRY_CHOICES,
        required=False,
        label='Indigenous country',
        help_text='Select the country associated with your Indigenous / First Nations / Native identity.',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    race_other = forms.CharField(
        required=False,
        max_length=RACE_OTHER_MAX_LENGTH,
        label='Describe your background',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional'}),
    )
    address_line = forms.CharField(
        required=False,
        max_length=ADDRESS_LINE_MAX_LENGTH,
        label='Street address',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    address_line_2 = forms.CharField(
        required=False,
        max_length=ADDRESS_LINE_MAX_LENGTH,
        label='Apartment, unit or suite (optional)',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    city = forms.CharField(
        required=False,
        max_length=200,
        label='City or town',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    state = forms.CharField(
        required=False,
        max_length=100,
        label='State / province',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    county = forms.CharField(
        required=False,
        max_length=200,
        label='County',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    postal_code = forms.CharField(
        required=False,
        max_length=POSTAL_CODE_MAX_LENGTH,
        label='Postal / ZIP code',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    country = forms.ChoiceField(
        choices=COUNTRY_CHOICES,
        required=False,
        label='Country',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    class Meta:
        model = GrowerProfile
        fields = [
            'phone',
            'gender',
            'age',
            'race',
            'race_indigenous_country',
            'race_other',
            'address_line',
            'address_line_2',
            'city',
            'state',
            'county',
            'postal_code',
            'country',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name in ('phone', 'race', 'race_indigenous_country', 'country'):
                continue
            css_class = 'form-select' if isinstance(field.widget, forms.Select) else 'form-control'
            field.widget.attrs.update({'class': css_class})

    def clean(self):
        cleaned_data = super().clean()
        race = cleaned_data.get('race')
        indigenous_country = cleaned_data.get('race_indigenous_country')
        race_other = (cleaned_data.get('race_other') or '').strip()

        if race != RACE_INDIGENOUS:
            cleaned_data['race_indigenous_country'] = ''
        elif not indigenous_country:
            self.add_error(
                'race_indigenous_country',
                'Please select the country associated with your Indigenous / First Nations / Native identity.',
            )

        if race != RACE_ANOTHER_BACKGROUND:
            cleaned_data['race_other'] = ''
        else:
            cleaned_data['race_other'] = race_other

        for field, message in validate_grower_address(cleaned_data).items():
            self.add_error(field, message)

        return cleaned_data


class ResultsFilterForm(forms.Form):
    """
    Form for filtering grower results by year, project type, and result type.
    """
    year = forms.IntegerField(
        required=False,
        label='Year',
        widget=forms.Select(choices=[])
    )
    project_type = forms.ChoiceField(
        choices=LABEL_PROJECT_CHOICES,
        required=False,
        label='Project Type'
    )
    result_type = forms.ChoiceField(
        choices=[('', 'All')] + RESULT_TYPE_CHOICES,
        required=False,
        label='Result Test Type'
    )

    def __init__(self, *args, available_years=None, **kwargs):
        super().__init__(*args, **kwargs)

        years = sorted(available_years or [], reverse=True) or [date.today().year]
        self.fields['year'].widget.choices = [(y, str(y)) for y in years]

        for field in self.fields.values():
            if hasattr(field.widget, 'attrs'):
                field.widget.attrs.update({'class': 'form-select'})


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
    crop_type = forms.ChoiceField(
        choices=[('', 'Select Crop Type')] + CROP_TYPE_CHOICES,
        required=False,
        label='Crop Type',
        help_text='Type of crop grown'
    )
    crop_subtype = forms.ChoiceField(
        choices=[('', 'Select Subtype')] + CROP_SUBTYPE_CHOICES,
        required=False,
        label='Specify:',
        help_text='Specific crop subtype'
    )
    crop_subtype_other = forms.CharField(
        max_length=200,
        required=False,
        label='Other Crop Type',
        help_text='Specify other crop type'
    )
    small_grain_type = forms.CharField(
        max_length=200,
        required=False,
        label='Small Grain Type',
        help_text='Specify small grain type'
    )
    tillage_methods = forms.CharField(
        max_length=TILLAGE_METHODS_MAX_LENGTH,
        required=False,
        widget=forms.Textarea(
            attrs={
                'rows': 3,
                'placeholder': 'e.g., disk, shanks, basket weed, broad fork, harrow, etc.'}),
        label='Tillage Methods',
        help_text='Tillage = any type of mechanical disturbance of the soil')
    forage_varieties = forms.CharField(
        max_length=FORAGE_VARIETIES_MAX_LENGTH,
        required=False,
        label='Forage Varieties',
        help_text='For rangeland'
    )
    paddock_size = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
        label='Paddock size',
        help_text='For rangeland',
        widget=forms.NumberInput(attrs={'step': 'any', 'class': 'form-control'}),
    )
    paddock_size_unit = area_unit_field()
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

    # Orchard-specific crop type fields
    orchard_crop_type = forms.ChoiceField(
        choices=[('', 'Select Crop Type')] + ORCHARD_CROP_TYPE_CHOICES,
        required=False,
        label='Crop Type',
        help_text='Type of crop grown in orchard'
    )
    orchard_crop_specify = forms.CharField(
        max_length=200,
        required=False,
        label='',
        help_text='Specify the type'
    )

    # Crop varieties field for orchards
    crop_varieties = forms.CharField(
        max_length=CROP_VARIETIES_MAX_LENGTH,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Enter crop variety or varieties'}),
        label='Crop Variety(ies)',
        help_text='Specify the crop variety or varieties grown'
    )

    # Field measurement fields
    area_sampled = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=True,
        label='Area in field sampled',
        help_text='Total area sampled for this field',
        widget=forms.NumberInput(attrs={'step': 'any', 'class': 'form-control'}),
    )
    area_sampled_unit = area_unit_field()
    years_under_management = forms.IntegerField(
        required=True,
        min_value=YEARS_UNDER_MANAGEMENT_MIN,
        max_value=YEARS_UNDER_MANAGEMENT_MAX,
        label='Number of years under current type of management',
        help_text='Years this field has been under current management'
    )
    supports_dairy = forms.BooleanField(
        required=False,
        label='Supports Dairy',
        help_text='Does this field support dairy operations?'
    )
    is_confined_dairy = forms.BooleanField(
        required=False,
        label='Is Confined Dairy',
        help_text='Is this a confined dairy operation?'
    )
    measurement_comments = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        label='Field comments',
        help_text='General comments about the field'
    )

    class Meta:
        model = GrowerApplication
        fields = ['date_sampled']

    required_fields = [
        'farm_name',
        'field_name',
        'field_type',
        'date_sampled',
        'area_sampled',
        'years_under_management']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.initial.get('field_type') == 'range':
            self.fields['area_sampled'].label = 'Area in paddock sampled'

        area_value, area_unit = area_form_initial(
            self.initial.get('area_sampled'),
            self.initial.get('area_sampled_entered'),
            self.initial.get('area_sampled_unit'),
        )
        if area_value is not None:
            self.fields['area_sampled'].initial = area_value
            self.fields['area_sampled_unit'].initial = area_unit

        paddock_value, paddock_unit = area_form_initial(
            self.initial.get('paddock_size'),
            self.initial.get('paddock_size_entered'),
            self.initial.get('paddock_size_unit'),
        )
        if paddock_value is not None:
            self.fields['paddock_size'].initial = paddock_value
            self.fields['paddock_size_unit'].initial = paddock_unit

    def get_primary_layout(self):
        return [Fieldset('Farm Information',
                         Row(Column('farm_name'))),
                Fieldset('Field Information',
                         Row(Column('field_name')),
                         Row(Column('field_type')),
                         Div(css_id='field_specific_properties',
                             css_class='mt-3'),
                         Div(HTML('<h6>Crop Information</h6>'),
                             Row(Column('crop_type')),
                             Div(Row(Column('crop_subtype')),
                                 css_id='crop_subtype_container',
                                 css_class='nested-conditional',
                                 style='display:none;'),
                             Div(Row(Column('crop_subtype_other')),
                                 css_id='crop_subtype_other_container',
                                 css_class='nested-conditional',
                                 style='display:none;'),
                             Div(Row(Column('small_grain_type')),
                                 css_id='small_grain_container',
                                 css_class='nested-conditional',
                                 style='display:none;'),
                             Row(Column('tillage_methods')),
                             css_id='crop_type_fields',
                             css_class='field-specific',
                             style='display:none;'),
                         Div(HTML('<h6>Rangeland Information</h6>'),
                             Row(Column('forage_varieties')),
                             value_with_unit_row('paddock_size', 'paddock_size_unit'),
                             css_id='rangeland_fields',
                             css_class='field-specific',
                             style='display:none;'),
                         Div(Row(Column('rootstock_species')),
                             Row(Column('orchard_crop_type')),
                             Div(Row(Column('orchard_crop_specify')),
                                 css_id='orchard_crop_specify_container',
                                 css_class='nested-conditional',
                                 style='display:none;'),
                             Row(Column('crop_varieties')),
                             css_id='orchard_specific_fields',
                             css_class='field-specific',
                             style='display:none;')),
                Fieldset('Application Details',
                         Row(Column('date_sampled'))),
                Fieldset('Field Measurements',
                         HTML(
                             '<p class="text-muted">Enter measurement information '
                             'for this field. These values will apply to all '
                             'transects.</p>'
                         ),
                         Row(
                             Div(
                                 Row(
                                     Column('area_sampled', css_class='col-md-8'),
                                     Column('area_sampled_unit', css_class='col-md-4'),
                                 ),
                                 css_class='col-md-6 measurement-with-unit-row',
                             ),
                             Column('years_under_management', css_class='col-md-6'),
                         ),
                         Div(Row(Column('supports_dairy',
                                        css_class='col-md-6')),
                             Div(Row(Column('is_confined_dairy',
                                            css_class='col-md-6')),
                                 css_id='confined_dairy_field',
                                 style='display:none;'),
                             css_id='dairy_fields',
                             css_class='non-orchard-only'),
                         Row(Column('measurement_comments'))),
                Submit('submit',
                       'Next: Field Information',
                       css_class='btn btn-primary btn-lg')]

    def clean(self):
        cleaned_data = super().clean()

        field_type = cleaned_data.get('field_type')

        capture_area_measurement(
            cleaned_data,
            value_key='area_sampled',
            unit_key='area_sampled_unit',
            entered_key='area_sampled_entered',
            canonical_key='area_sampled_ha',
        )
        area_sampled_ha = cleaned_data.get('area_sampled_ha')
        if area_sampled_ha is not None:
            if area_sampled_ha < AREA_SAMPLED_HA_MIN or area_sampled_ha > AREA_SAMPLED_HA_MAX:
                self.add_error(
                    'area_sampled',
                    f'Area must be between {AREA_SAMPLED_HA_MIN} and {AREA_SAMPLED_HA_MAX} hectares after conversion.',
                )

        capture_area_measurement(
            cleaned_data,
            value_key='paddock_size',
            unit_key='paddock_size_unit',
            entered_key='paddock_size_entered',
            canonical_key='paddock_size_ha',
        )
        paddock_size_ha = cleaned_data.get('paddock_size_ha')
        if paddock_size_ha is not None:
            if paddock_size_ha < AREA_SAMPLED_HA_MIN or paddock_size_ha > AREA_SAMPLED_HA_MAX:
                self.add_error(
                    'paddock_size',
                    f'Paddock size must be between {AREA_SAMPLED_HA_MIN} and {AREA_SAMPLED_HA_MAX} hectares after conversion.',
                )

        if field_type == 'crop':
            crop_type = cleaned_data.get('crop_type', '').strip()
            if not crop_type:
                self.add_error('crop_type', 'Crop type is required for crop fields.')
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
    tillage_depth = forms.DecimalField(
        required=False,
        min_value=0,
        max_value=500,
        decimal_places=2,
        label='Tillage depth',
        widget=forms.NumberInput(attrs={'step': 'any', 'class': 'form-control'}),
    )
    tillage_depth_unit = depth_unit_field()
    cover_crop_termination = forms.ChoiceField(
        choices=[('', 'Select Method')] + COVER_CROP_TERMINATION_CHOICES,
        required=False,
        label='Cover Crop Termination',
        help_text='Method used to terminate cover crops'
    )
    cover_crop_termination_other = forms.CharField(
        max_length=200,
        required=False,
        label='Other Termination Method',
        help_text='Specify other termination method'
    )
    organic_amendment_types = forms.ChoiceField(
        choices=[('', 'Select Type')] + ORGANIC_AMENDMENT_CHOICES,
        required=False,
        label='Organic Amendment Types',
        help_text='Type of organic amendments used'
    )
    organic_amendment_other = forms.CharField(
        max_length=200,
        required=False,
        label='Other Amendment Type',
        help_text='Specify other organic amendment type'
    )

    grazer_types = forms.ChoiceField(
        choices=[('', 'Select Type')] + GRAZER_TYPES_CHOICES,
        required=False,
        label='Grazer Types',
        help_text='Type of animals used for grazing'
    )
    grazer_types_other = forms.CharField(
        max_length=200,
        required=False,
        label='Other Grazer Type',
        help_text='Specify other grazer type'
    )
    ground_cover_management = forms.ChoiceField(
        choices=[('', 'Select Method')] + GROUND_COVER_MANAGEMENT_CHOICES,
        required=False,
        label='Ground Cover Management',
        help_text='Method used to manage ground cover'
    )
    ground_cover_management_other = forms.CharField(
        max_length=200,
        required=False,
        label='Other Management Method',
        help_text='Specify other ground cover management method'
    )
    uses_broad_fork = forms.BooleanField(
        required=False,
        label='Broad Fork',
        help_text='Uses broad fork cultivation'
    )

    class Meta:
        model = ManagementPractices
        fields = [
            'uses_tillage', 'tillage_depth_entered', 'tillage_depth_unit',
            'uses_cover_crop', 'cover_crop_termination', 'cover_crop_termination_other',
            'uses_synthetic_fertilizers', 'uses_synthetic_insecticides',
            'uses_synthetic_herbicides', 'uses_synthetic_fungicides',
            'uses_organic_amendments', 'organic_amendment_types', 'organic_amendment_other',
            'grazed_current_year', 'grazed_by_livestock_plan', 'not_grazed_comments',
            'applies_insecticides_dewormers', 'insecticide_dewormer_frequency', 'insecticide_dewormer_comments',
            'grazer_types', 'grazer_types_other',
            'allows_ground_cover', 'ground_cover_management', 'ground_cover_management_other', 'tills_between_rows'
        ]

    required_fields = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            entered, unit = depth_form_initial(
                self.instance.tillage_depth_cm,
                self.instance.tillage_depth_entered,
                self.instance.tillage_depth_unit,
            )
            if entered is not None:
                self.fields['tillage_depth'].initial = entered
                self.fields['tillage_depth_unit'].initial = unit
        else:
            entered, unit = depth_form_initial(
                self.initial.get('tillage_depth_cm'),
                self.initial.get('tillage_depth_entered'),
                self.initial.get('tillage_depth_unit'),
            )
            if entered is not None:
                self.fields['tillage_depth'].initial = entered
                self.fields['tillage_depth_unit'].initial = unit

    def get_primary_layout(self):
        return [
            Div(
                Fieldset(
                    'Tillage Practices',
                    Row(Column('uses_tillage')),
                    Div(
                        value_with_unit_row('tillage_depth', 'tillage_depth_unit'),
                        css_id='tillage_depth_field',
                        style='display:none;'
                    )
                ),
                css_id='tillage_practices_section',
                css_class='non-orchard-only non-rangeland-only'
            ),
            Div(
                Fieldset(
                    'Cover Crops',
                    Row(Column('uses_cover_crop')),
                    Div(
                        Row(Column('cover_crop_termination')),
                        Div(
                            Row(Column('cover_crop_termination_other')),
                            css_id='cover_crop_termination_other_container',
                            style='display:none;'
                        ),
                        css_id='cover_crop_fields',
                        style='display:none;'
                    )
                ),
                css_class=''
            ),
            Div(
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
                css_class=''
            ),
            Div(
                Fieldset(
                    'Organic Amendments',
                    Row(Column('uses_organic_amendments')),
                    Div(
                        Row(Column('organic_amendment_types')),
                        Div(
                            Row(Column('organic_amendment_other')),
                            css_id='organic_amendment_other_container',
                            style='display:none;'
                        ),
                        css_id='organic_amendment_fields',
                        style='display:none;'
                    )
                ),
                css_class=''
            ),
            Div(
                Fieldset(
                    'Grazing Practices',
                    Row(Column('grazed_current_year')),
                    Row(Column('grazed_by_livestock_plan')),
                    Div(
                        Row(Column('not_grazed_comments')),
                        css_id='not_grazed_comments_container',
                        style='display:none;'
                    ),
                    HTML('<hr />'),
                    Row(Column('applies_insecticides_dewormers')),
                    Div(
                        Row(
                            Column('insecticide_dewormer_frequency', css_class='col-md-6'),
                            Column('insecticide_dewormer_comments', css_class='col-md-6')
                        ),
                        css_id='insecticide_dewormer_fields',
                        style='display:none;'
                    ),
                    Div(
                        Row(Column('grazer_types')),
                        Div(
                            Row(Column('grazer_types_other')),
                            css_id='grazer_types_other_container',
                            style='display:none;'
                        ),
                        css_id='grazing_fields',
                        style='display:none;'
                    )
                ),
                css_class=''
            ),
            Fieldset(
                'Specific Practices',
                Row(Column('allows_ground_cover')),
                Div(
                    Row(Column('ground_cover_management')),
                    Div(
                        Row(Column('ground_cover_management_other')),
                        css_id='ground_cover_management_other_container',
                        style='display:none;'
                    ),
                    css_id='ground_cover_fields',
                    style='display:none;'
                ),
                Row(Column('tills_between_rows')),
                Div(
                    css_id='orchard_tillage_depth_mount',
                    style='display:none;'
                ),
                css_id='orchard_practices',
                css_class='orchard-only'
            ),
            Submit('submit', 'Next: Transect Codes', css_class='btn btn-primary')
        ]

    def clean(self):
        cleaned_data = super().clean()
        capture_depth_measurement(
            cleaned_data,
            value_key='tillage_depth',
            unit_key='tillage_depth_unit',
            entered_key='tillage_depth_entered',
            canonical_key='tillage_depth_cm',
        )
        return cleaned_data

    def save(self, commit=True):
        practices = super().save(commit=False)
        practices.tillage_depth_cm = self.cleaned_data.get('tillage_depth_cm')
        if commit:
            practices.save()
        return practices


class TransectCodesForm(forms.Form):
    """Form for entering transect codes and GPS coordinates in Step 3"""

    _COORDINATE_WIDGET_ATTRS = {'step': 'any', 'class': 'form-control'}

    def __init__(self, *args, **kwargs):
        self.field_type = kwargs.pop('field_type', None)
        self.for_application = kwargs.pop('for_application', None)
        super().__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.form_action = '.'
        self.helper.form_tag = False
        self.helper.layout = Layout(
            *self.get_primary_layout(),
        )
        self.use_required_attribute = False

    transect_code_1 = forms.CharField(
        max_length=20,
        required=False,
        label='Transect Code',
        widget=forms.TextInput(attrs={'placeholder': 'Enter transect code'})
    )
    transect_code_2 = forms.CharField(
        max_length=20,
        required=False,
        label='Transect Code',
        widget=forms.TextInput(attrs={'placeholder': 'Enter transect code'})
    )
    transect_code_3 = forms.CharField(
        max_length=20,
        required=False,
        label='Transect Code',
        widget=forms.TextInput(attrs={'placeholder': 'Enter transect code'})
    )
    transect_code_4 = forms.CharField(
        max_length=20,
        required=False,
        label='Transect Code',
        widget=forms.TextInput(attrs={'placeholder': 'Enter transect code'})
    )

    transect_1_latitude = forms.FloatField(
        required=False,
        label='Latitude',
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
        widget=forms.NumberInput(attrs={**_COORDINATE_WIDGET_ATTRS, 'placeholder': '44.660611'}),
    )
    transect_1_longitude = forms.FloatField(
        required=False,
        label='Longitude',
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
        widget=forms.NumberInput(attrs={**_COORDINATE_WIDGET_ATTRS, 'placeholder': '-96.813411'}),
    )
    transect_2_latitude = forms.FloatField(
        required=False,
        label='Latitude',
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
        widget=forms.NumberInput(attrs={**_COORDINATE_WIDGET_ATTRS, 'placeholder': '44.660611'}),
    )
    transect_2_longitude = forms.FloatField(
        required=False,
        label='Longitude',
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
        widget=forms.NumberInput(attrs={**_COORDINATE_WIDGET_ATTRS, 'placeholder': '-96.813411'}),
    )
    transect_3_latitude = forms.FloatField(
        required=False,
        label='Latitude',
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
        widget=forms.NumberInput(attrs={**_COORDINATE_WIDGET_ATTRS, 'placeholder': '44.660611'}),
    )
    transect_3_longitude = forms.FloatField(
        required=False,
        label='Longitude',
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
        widget=forms.NumberInput(attrs={**_COORDINATE_WIDGET_ATTRS, 'placeholder': '-96.813411'}),
    )
    transect_4_latitude = forms.FloatField(
        required=False,
        label='Latitude',
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
        widget=forms.NumberInput(attrs={**_COORDINATE_WIDGET_ATTRS, 'placeholder': '44.660611'}),
    )
    transect_4_longitude = forms.FloatField(
        required=False,
        label='Longitude',
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
        widget=forms.NumberInput(attrs={**_COORDINATE_WIDGET_ATTRS, 'placeholder': '-96.813411'}),
    )

    def _transect_row_layout(self, slot):
        applicable = ' <span class="text-muted fw-normal">(if applicable)</span>' if slot > 1 else ''
        return [
            HTML(f'<div class="transect-location-row transect-location-card" data-slot="{slot}">'),
            HTML(
                f'<div class="transect-location-card__header">'
                f'<span class="transect-location-card__badge">{slot}</span>'
                f'<span class="transect-location-card__title">Transect location {slot}{applicable}</span>'
                f'</div>'
            ),
            Row(
                Column(f'transect_code_{slot}', css_class='col-md-4'),
                Column(f'transect_{slot}_latitude', css_class='col-md-4'),
                Column(f'transect_{slot}_longitude', css_class='col-md-4'),
            ),
            HTML('</div>'),
        ]

    def get_primary_layout(self):
        rows = []
        for slot in range(1, 5):
            rows.extend(self._transect_row_layout(slot))

        return [
            HTML(
                '<p class="text-muted mb-3">Enter one or more transects (up to 4). '
                'Transect location 1 is required. Add additional locations only if you have more '
                'transect codes. For each location, enter the transect code, latitude, and longitude '
                'together, then review the marker(s) on the map.</p>'
            ),
            HTML('<div id="transect-location-fields" class="transect-location-fields">'),
            *rows,
            HTML('</div>'),
            HTML(
                '<button type="button" id="add-transect-location" class="btn btn-outline-secondary btn-sm mt-2">'
                '<i class="fas fa-plus"></i> Add another transect</button>'
            ),
        ]

    def clean(self):
        cleaned_data = super().clean()
        complete_transects = []

        for i in range(1, 5):
            code = (cleaned_data.get(f'transect_code_{i}') or '').strip()
            lat = cleaned_data.get(f'transect_{i}_latitude')
            lng = cleaned_data.get(f'transect_{i}_longitude')
            has_any = bool(code) or lat is not None or lng is not None

            if not has_any:
                cleaned_data[f'transect_code_{i}'] = ''
                cleaned_data[f'transect_{i}_latitude'] = None
                cleaned_data[f'transect_{i}_longitude'] = None
                continue

            if not code:
                self.add_error(
                    f'transect_code_{i}',
                    'Transect code is required when entering data for this location.',
                )
            if lat is None:
                self.add_error(
                    f'transect_{i}_latitude',
                    'Latitude is required when entering data for this location.',
                )
            elif lat < -90 or lat > 90:
                self.add_error(f'transect_{i}_latitude', 'Latitude must be between -90 and 90.')

            if lng is None:
                self.add_error(
                    f'transect_{i}_longitude',
                    'Longitude is required when entering data for this location.',
                )
            elif lng < -180 or lng > 180:
                self.add_error(f'transect_{i}_longitude', 'Longitude must be between -180 and 180.')

            if not code or lat is None or lng is None:
                continue

            cleaned_data[f'transect_{i}_latitude'] = round(float(lat), 6)
            cleaned_data[f'transect_{i}_longitude'] = round(float(lng), 6)
            lat = cleaned_data[f'transect_{i}_latitude']
            lng = cleaned_data[f'transect_{i}_longitude']

            try:
                transect_obj = SampleCode.objects.get(code=code, is_active=True)

                if transect_obj.is_used:
                    same_app = (
                        self.for_application is not None
                        and transect_obj.used_in_application_id == self.for_application.pk
                    )
                    if not same_app:
                        other = transect_obj.used_in_application
                        submission = (
                            other.submission_code if other else 'another application'
                        )
                        self.add_error(
                            f'transect_code_{i}',
                            f'Transect code "{code}" has already been used in application {submission}.',
                        )
            except SampleCode.DoesNotExist:
                self.add_error(f'transect_code_{i}', f'Transect code "{code}" is not valid.')

            if code in complete_transects:
                self.add_error(f'transect_code_{i}', f'Duplicate transect code "{code}".')
            else:
                complete_transects.append(code)

        if not complete_transects:
            raise forms.ValidationError(
                'At least one complete transect (code, latitude, and longitude) is required.',
            )

        return cleaned_data


class GrazingEventForm(ModelFormMixin):
    class Meta:
        model = GrazingEvent
        fields = ['start_date']

    required_fields = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['start_date'].widget = Html5DateInput()
        self.fields['start_date'].label = 'Start Date (estimate is acceptable)'
        self.fields['start_date'].required = False
        self.helper.form_tag = False

    def get_primary_layout(self):
        return [
            Row(Column('start_date'))
        ]


class GrazingEventAnimalForm(forms.ModelForm):
    """Form for individual animal entries within a grazing event"""

    average_weight = forms.DecimalField(
        required=False,
        min_value=0.1,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'step': 'any'}),
    )
    duration_days = forms.DecimalField(
        required=False,
        min_value=0.1,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'step': 'any'}),
    )
    rest_period_days = forms.DecimalField(
        required=False,
        min_value=0,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'step': 'any'}),
    )
    average_weight_unit = weight_unit_field()
    duration_unit = time_unit_field()
    rest_period_unit = time_unit_field()

    class Meta:
        model = GrazingEventAnimal
        fields = [
            'class_of_animal',
            'number_of_animals',
            'average_weight_entered',
            'average_weight_unit',
            'duration_days',
            'duration_entered',
            'duration_unit',
            'rest_period_days',
            'rest_period_entered',
            'rest_period_unit',
        ]

    def save(self, commit=True):
        animal = super().save(commit=False)
        animal.average_weight_kg = self.cleaned_data.get('average_weight_kg')
        if commit:
            animal.save()
        return animal

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['average_weight'].label = 'Average weight'
        self.fields['duration_days'].label = 'Grazing duration'
        self.fields['rest_period_days'].label = 'Rest period'
        for field in self.fields.values():
            field.required = False
            if not isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-control form-control-sm'})

        for unit_field in ('average_weight_unit', 'duration_unit', 'rest_period_unit'):
            self.fields[unit_field].required = True
            self.fields[unit_field].widget.attrs.update({
                'class': 'form-select form-select-sm measurement-unit-select',
            })

        if self.instance and self.instance.pk and not self.is_bound:
            weight_value, weight_unit = grazing_form_initial(
                self.instance.average_weight_kg,
                self.instance.average_weight_entered,
                self.instance.average_weight_unit,
                from_canonical='weight',
            )
            if weight_value is not None:
                self.fields['average_weight'].initial = weight_value
            self.fields['average_weight_unit'].initial = weight_unit

            duration_value, duration_unit = grazing_form_initial(
                self.instance.duration_days,
                self.instance.duration_entered,
                self.instance.duration_unit,
                from_canonical='duration',
            )
            if duration_value is not None:
                self.fields['duration_days'].initial = duration_value
            self.fields['duration_unit'].initial = duration_unit

            rest_value, rest_unit = grazing_form_initial(
                self.instance.rest_period_days,
                self.instance.rest_period_entered,
                self.instance.rest_period_unit,
                from_canonical='duration',
            )
            if rest_value is not None:
                self.fields['rest_period_days'].initial = rest_value
            self.fields['rest_period_unit'].initial = rest_unit
        elif not self.is_bound:
            self.fields['average_weight_unit'].initial = DEFAULT_WEIGHT_UNIT
            self.fields['duration_unit'].initial = DEFAULT_TIME_UNIT
            self.fields['rest_period_unit'].initial = DEFAULT_TIME_UNIT

    def clean(self):
        """Validate that if any field is filled, all required fields must be filled"""
        cleaned_data = super().clean()

        weight_unit = cleaned_data.get('average_weight_unit') or DEFAULT_WEIGHT_UNIT
        duration_unit = cleaned_data.get('duration_unit') or DEFAULT_TIME_UNIT
        rest_unit = cleaned_data.get('rest_period_unit') or DEFAULT_TIME_UNIT
        cleaned_data['average_weight_unit'] = weight_unit
        cleaned_data['duration_unit'] = duration_unit
        cleaned_data['rest_period_unit'] = rest_unit

        capture_weight_measurement(
            cleaned_data,
            value_key='average_weight',
            unit_key='average_weight_unit',
            entered_key='average_weight_entered',
            canonical_key='average_weight_kg',
        )
        if cleaned_data.get('average_weight_kg') not in (None, ''):
            converted_weight = cleaned_data['average_weight_kg']
            if converted_weight < AVERAGE_WEIGHT_KG_MIN or converted_weight > AVERAGE_WEIGHT_KG_MAX:
                self.add_error(
                    'average_weight',
                    f'Average weight must be between {AVERAGE_WEIGHT_KG_MIN} and {AVERAGE_WEIGHT_KG_MAX} kg after conversion.',
                )

        capture_duration_measurement(
            cleaned_data,
            value_key='duration_days',
            unit_key='duration_unit',
            entered_key='duration_entered',
            canonical_key='duration_days',
        )
        if cleaned_data.get('duration_days') not in (None, ''):
            converted_duration = cleaned_data['duration_days']
            if converted_duration < DURATION_DAYS_MIN or converted_duration > DURATION_DAYS_MAX:
                self.add_error(
                    'duration_days',
                    f'Grazing duration must be between {DURATION_DAYS_MIN} and {DURATION_DAYS_MAX} days after conversion.',
                )

        capture_duration_measurement(
            cleaned_data,
            value_key='rest_period_days',
            unit_key='rest_period_unit',
            entered_key='rest_period_entered',
            canonical_key='rest_period_days',
        )
        if cleaned_data.get('rest_period_days') not in (None, ''):
            converted_rest = cleaned_data['rest_period_days']
            if converted_rest < REST_PERIOD_DAYS_MIN or converted_rest > REST_PERIOD_DAYS_MAX:
                self.add_error(
                    'rest_period_days',
                    f'Rest period must be between {REST_PERIOD_DAYS_MIN} and {REST_PERIOD_DAYS_MAX} days after conversion.',
                )

        class_of_animal = cleaned_data.get('class_of_animal',
                                           '').strip() if cleaned_data.get('class_of_animal') else ''
        number_of_animals = cleaned_data.get('number_of_animals')
        average_weight = cleaned_data.get('average_weight_kg')
        duration_days = cleaned_data.get('duration_days')
        rest_period_days = cleaned_data.get('rest_period_days')

        has_any_value = any([
            class_of_animal,
            number_of_animals not in (None, ''),
            average_weight not in (None, ''),
            duration_days not in (None, ''),
            rest_period_days not in (None, '')
        ])

        if not has_any_value:
            return cleaned_data

        required_fields = ['class_of_animal', 'number_of_animals', 'average_weight',
                           'duration_days', 'rest_period_days']
        missing_fields = []
        for field_name in required_fields:
            value = cleaned_data.get(field_name)
            if value in (None, '', []):
                missing_fields.append(self.fields[field_name].label or field_name)

        if missing_fields:
            raise forms.ValidationError(
                f'If you fill in any field, all fields must be completed. Missing: {", ".join(missing_fields)}'
            )

        return cleaned_data


GrazingEventAnimalFormSet = inlineformset_factory(
    GrazingEvent,
    GrazingEventAnimal,
    form=GrazingEventAnimalForm,
    extra=1,
    min_num=0,
    max_num=MAX_ANIMAL_ENTRIES_PER_GRAZING_EVENT,
    can_delete=True,
    validate_max=True
)


class TransectMeasurementGeneralForm(forms.ModelForm):
    class Meta:
        model = TransectMeasurement
        fields = ['general_time', 'temperature_c', 'wind_speed_ms', 'field_condition']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['general_time'].required = True
        self.fields['temperature_c'].required = True
        self.fields['wind_speed_ms'].required = True
        self.fields['field_condition'].required = True


class DropPlateReadingForm(forms.ModelForm):
    class Meta:
        model = DropPlateReading
        fields = ['distance_m', 'value']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['value'].required = True


DropPlateFormSet = inlineformset_factory(
    TransectMeasurement,
    DropPlateReading,
    form=DropPlateReadingForm,
    extra=0,
    can_delete=False,
)


class VegetationReadingForm(forms.ModelForm):
    class Meta:
        model = VegetationReading
        fields = ['metric', 'position_m', 'value']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['value'].required = True


VegetationFormSet = inlineformset_factory(
    TransectMeasurement,
    VegetationReading,
    form=VegetationReadingForm,
    extra=0,
    can_delete=False,
)


class SoilReadingForm(forms.ModelForm):
    class Meta:
        model = SoilReading
        fields = ['metric', 'position_m', 'value']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['value'].required = True


SoilFormSet = inlineformset_factory(
    TransectMeasurement,
    SoilReading,
    form=SoilReadingForm,
    extra=0,
    can_delete=False,
)


class SoilCompactionReadingForm(forms.ModelForm):
    class Meta:
        model = SoilCompactionReading
        fields = ['position_m', 'max_value', 'score', 'hp']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['max_value'].required = True
        self.fields['score'].required = True
        self.fields['hp'].required = True


SoilCompactionFormSet = inlineformset_factory(
    TransectMeasurement,
    SoilCompactionReading,
    form=SoilCompactionReadingForm,
    extra=0,
    can_delete=False,
)


class InfiltrometerReadingForm(forms.ModelForm):
    class Meta:
        model = InfiltrometerReading
        fields = ['time_mark', 'volume_ml']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['volume_ml'].required = True


InfiltrometerFormSet = inlineformset_factory(
    TransectMeasurement,
    InfiltrometerReading,
    form=InfiltrometerReadingForm,
    extra=0,
    can_delete=False,
)


class InfiltrationRingReadingForm(forms.ModelForm):
    class Meta:
        model = InfiltrationRingReading
        fields = ['pour_number', 'start_depth_cm', 'infiltration_time_sec',
                  'depth_after_15min_cm', 'change_in_depth_cm']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['start_depth_cm'].required = True
        self.fields['infiltration_time_sec'].required = True
        self.fields['depth_after_15min_cm'].required = True
        self.fields['change_in_depth_cm'].required = True


InfiltrationRingFormSet = inlineformset_factory(
    TransectMeasurement,
    InfiltrationRingReading,
    form=InfiltrationRingReadingForm,
    extra=0,
    can_delete=False,
)
