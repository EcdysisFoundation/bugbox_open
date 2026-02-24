from datetime import date
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Column, Div, Fieldset, Layout, Row, Submit
from django import forms
from django.contrib.auth import get_user_model
from django.forms import inlineformset_factory

from bugbox3.core.forms import Html5DateInput, ModelFormMixin

from ...constants import (
    ACRES_SAMPLED_MAX,
    ACRES_SAMPLED_MIN,
    AGE_MAX,
    AGE_MIN,
    COVER_CROP_TERMINATION_CHOICES,
    CROP_SUBTYPE_CHOICES,
    CROP_TYPE_CHOICES,
    CROP_VARIETIES_MAX_LENGTH,
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
    RACE_CHOICES,
    RESULT_TYPE_CHOICES,
    ROOTSTOCK_SPECIES_MAX_LENGTH,
    TILLAGE_METHODS_MAX_LENGTH,
    TRANSITIONAL_STATUS_CHOICES,
    YEARS_UNDER_MANAGEMENT_MAX,
    YEARS_UNDER_MANAGEMENT_MIN,
)
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
        label='Result Type'
    )

    def __init__(self, *args, available_years=None, **kwargs):
        super().__init__(*args, **kwargs)

        years = sorted(available_years or [], reverse=True) or [date.today().year]
        self.fields['year'].widget.choices = [(y, str(y)) for y in years]

        for field in self.fields.values():
            if hasattr(field.widget, 'attrs'):
                field.widget.attrs.update({'class': 'form-select'})

        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.form_class = 'row g-3'
        self.helper.form_id = 'resultsFilterForm'

        self.helper.layout = Layout(
            Row(
                Column('year', css_class='col-md-4'),
                Column('project_type', css_class='col-md-4'),
                Column('result_type', css_class='col-md-4'),
            ),
        )


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
    paddock_size = forms.CharField(
        max_length=PADDOCK_SIZE_MAX_LENGTH,
        required=False,
        label='Paddock size (acres)',
        help_text='For rangeland'
    )
    pasture_size = forms.CharField(
        max_length=PADDOCK_SIZE_MAX_LENGTH,
        required=False,
        label='Pasture size (acres)',
        help_text='Total pasture size in acres'
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
    acres_sampled = forms.DecimalField(
        max_digits=8,
        decimal_places=2,
        required=True,
        min_value=ACRES_SAMPLED_MIN,
        max_value=ACRES_SAMPLED_MAX,
        label='Number of acres in field sampled',
        help_text='Total acres sampled for this field'
    )
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
        'acres_sampled',
        'years_under_management']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.initial.get('field_type') == 'range':
            self.fields['acres_sampled'].label = 'Acres in paddock sampled'

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
                             Row(Column('paddock_size',
                                        css_class='col-md-6'),
                                 Column('pasture_size',
                                 css_class='col-md-6')),
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
                         Row(Column('acres_sampled',
                                    css_class='col-md-6'),
                             Column('years_under_management',
                                    css_class='col-md-6')),
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
            'uses_tillage', 'tillage_depth',
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

    def get_primary_layout(self):
        return [
            Div(
                Fieldset(
                    'Tillage Practices',
                    Row(Column('uses_tillage')),
                    Div(
                        Row(Column('tillage_depth')),
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


class TransectCodesForm(forms.Form):
    """Form for entering transect codes in Step 3"""

    def __init__(self, *args, **kwargs):
        self.field_type = kwargs.pop('field_type', None)
        super().__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.form_action = '.'
        self.helper.layout = Layout(
            *self.get_primary_layout(),
        )
        self.use_required_attribute = False

    transect_code_1 = forms.CharField(
        max_length=20,
        required=False,
        label='Transect Code 1',
        help_text='Optional - at least one transect code is required',
        widget=forms.TextInput(attrs={'placeholder': 'Enter transect code'})
    )
    transect_code_2 = forms.CharField(
        max_length=20,
        required=False,
        label='Transect Code 2',
        widget=forms.TextInput(attrs={'placeholder': 'Enter transect code'})
    )
    transect_code_3 = forms.CharField(
        max_length=20,
        required=False,
        label='Transect Code 3',
        widget=forms.TextInput(attrs={'placeholder': 'Enter transect code'})
    )
    transect_code_4 = forms.CharField(
        max_length=20,
        required=False,
        label='Transect Code 4',
        widget=forms.TextInput(attrs={'placeholder': 'Enter transect code'})
    )

    # Hidden coordinate fields
    transect_1_latitude = forms.DecimalField(required=False, widget=forms.HiddenInput())
    transect_1_longitude = forms.DecimalField(required=False, widget=forms.HiddenInput())
    transect_2_latitude = forms.DecimalField(required=False, widget=forms.HiddenInput())
    transect_2_longitude = forms.DecimalField(required=False, widget=forms.HiddenInput())
    transect_3_latitude = forms.DecimalField(required=False, widget=forms.HiddenInput())
    transect_3_longitude = forms.DecimalField(required=False, widget=forms.HiddenInput())
    transect_4_latitude = forms.DecimalField(required=False, widget=forms.HiddenInput())
    transect_4_longitude = forms.DecimalField(required=False, widget=forms.HiddenInput())

    def get_primary_layout(self):
        button_text = 'Next: Transect Measurements'

        return [
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
                ),
                'transect_1_latitude',
                'transect_1_longitude',
                'transect_2_latitude',
                'transect_2_longitude',
                'transect_3_latitude',
                'transect_3_longitude',
                'transect_4_latitude',
                'transect_4_longitude',
                Submit('submit', button_text, css_class='btn btn-primary')
            )
        ]

    def clean(self):
        cleaned_data = super().clean()
        transect_codes = []

        for i in range(1, 5):
            code = cleaned_data.get(f'transect_code_{i}', '').strip()
            if code:
                try:
                    transect_obj = SampleCode.objects.get(code=code, is_active=True)

                    if transect_obj.is_used:
                        self.add_error(
                            f'transect_code_{i}',
                            f'Transect code "{code}" has already been used in a submitted application.'
                        )
                except SampleCode.DoesNotExist:
                    self.add_error(f'transect_code_{i}', f'Transect code "{code}" is not valid.')

                if code in transect_codes:
                    self.add_error(f'transect_code_{i}', f'Duplicate transect code "{code}".')
                transect_codes.append(code)

        if not transect_codes:
            raise forms.ValidationError('At least one transect code is required.')

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

    class Meta:
        model = GrazingEventAnimal
        fields = ['class_of_animal', 'number_of_animals', 'average_weight_lbs',
                  'duration_days', 'rest_period_days']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['duration_days'].label = 'Grazing days'
        for field in self.fields.values():
            field.required = False
            field.widget.attrs.update({'class': 'form-control form-control-sm'})

    def clean(self):
        """Validate that if any field is filled, all required fields must be filled"""
        cleaned_data = super().clean()

        class_of_animal = cleaned_data.get('class_of_animal',
                                           '').strip() if cleaned_data.get('class_of_animal') else ''
        number_of_animals = cleaned_data.get('number_of_animals')
        average_weight_lbs = cleaned_data.get('average_weight_lbs')
        duration_days = cleaned_data.get('duration_days')
        rest_period_days = cleaned_data.get('rest_period_days')

        has_any_value = any([
            class_of_animal,
            number_of_animals not in (None, ''),
            average_weight_lbs not in (None, ''),
            duration_days not in (None, ''),
            rest_period_days not in (None, '')
        ])

        if not has_any_value:
            return cleaned_data

        required_fields = ['class_of_animal', 'number_of_animals', 'average_weight_lbs',
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
