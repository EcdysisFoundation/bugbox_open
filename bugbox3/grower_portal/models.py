from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import uuid

from .constants import (
    GENDER_CHOICES, RACE_CHOICES, FIELD_TYPE_CHOICES,
    TRANSITIONAL_STATUS_CHOICES, INSECTICIDE_FREQUENCY_CHOICES,
    CSV_IMPORT_STATUS_CHOICES, CROP_TYPE_CHOICES, CROP_SUBTYPE_CHOICES,
    COVER_CROP_TERMINATION_CHOICES, ORGANIC_AMENDMENT_CHOICES,
    GRAZER_TYPES_CHOICES, GROUND_COVER_MANAGEMENT_CHOICES,
    AGE_MIN, AGE_MAX, LATITUDE_MIN, LATITUDE_MAX,
    LONGITUDE_MIN, LONGITUDE_MAX, GRAZING_EVENT_NUMBER_MIN,
    GRAZING_EVENT_NUMBER_MAX, REST_PERIOD_DAYS_MIN,
    REST_PERIOD_DAYS_MAX, NUMBER_OF_ANIMALS_MIN,
    NUMBER_OF_ANIMALS_MAX, AVERAGE_WEIGHT_MIN,
    AVERAGE_WEIGHT_MAX, DURATION_DAYS_MIN, DURATION_DAYS_MAX,
    PHONE_MAX_LENGTH, FARM_NAME_MAX_LENGTH, FIELD_NAME_MAX_LENGTH,
    CROP_VARIETY_MAX_LENGTH, CROP_VARIETIES_MAX_LENGTH, FORAGE_VARIETIES_MAX_LENGTH,
    PADDOCK_SIZE_MAX_LENGTH, ROOTSTOCK_SPECIES_MAX_LENGTH,
    TILLAGE_DEPTH_MAX_LENGTH, TILLAGE_METHODS_MAX_LENGTH, COVER_CROP_TERMINATION_MAX_LENGTH,
    ORGANIC_AMENDMENT_TYPES_MAX_LENGTH, GRAZER_TYPES_MAX_LENGTH,
    INSECTICIDE_FREQUENCY_MAX_LENGTH, INSECTICIDE_COMMENTS_MAX_LENGTH,
    GROUND_COVER_MANAGEMENT_MAX_LENGTH, TRANSECT_CODE_MAX_LENGTH,
    SUBMISSION_CODE_MAX_LENGTH, CLASS_OF_ANIMAL_MAX_LENGTH,
    CSV_FILENAME_MAX_LENGTH, STATUS_MAX_LENGTH, SUBMISSION_CODE_PREFIX,
    FIELD_INITIALS_MAX_LENGTH, GROWER_INITIALS_MAX_LENGTH,
    GROWER_INITIALS_DEFAULT, UUID_SUFFIX_LENGTH,
    ACRES_SAMPLED_MIN, ACRES_SAMPLED_MAX,
    YEARS_UNDER_MANAGEMENT_MIN, YEARS_UNDER_MANAGEMENT_MAX,
    DISTANCES_DROP_PLATE, POSITIONS_3POINT, INFILTROMETER_TIMES,
    FIELD_CONDITION_CHOICES, VEGETATION_METRIC_CHOICES, SOIL_METRIC_CHOICES
)

User = get_user_model()


class GrowerProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='grower_profile'
    )
    phone = models.CharField(
        max_length=PHONE_MAX_LENGTH,
        blank=True,
        null=True
    )
    gender = models.CharField(
        max_length=PHONE_MAX_LENGTH,
        choices=GENDER_CHOICES,
        blank=True,
        null=True
    )
    age = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text='Age in years',
        validators=[MinValueValidator(AGE_MIN), MaxValueValidator(AGE_MAX)]
    )
    race = models.CharField(
        max_length=STATUS_MAX_LENGTH,
        choices=RACE_CHOICES,
        blank=True,
        null=True
    )
    profile_completed = models.BooleanField(
        default=False,
        help_text='Whether the initial profile completion has been done'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Grower Profile')
        verbose_name_plural = _('Grower Profiles')
        permissions = [
            ('manage_grower_profiles', 'Can manage grower profiles'),
        ]

    def __str__(self):
        return f"{self.user.name} ({self.user.email})"


class Farm(models.Model):
    """Farm/organization entity - one grower can have multiple farms"""
    grower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='farms'
    )
    name = models.CharField(max_length=FARM_NAME_MAX_LENGTH)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Farm')
        verbose_name_plural = _('Farms')
        constraints = [
            models.UniqueConstraint(
                fields=['grower', 'name'],
                name='unique_grower_farm_name'
            )
        ]
        permissions = [
            ('manage_farms', 'Can manage farms'),
        ]
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.grower.name})"


class Field(models.Model):
    """Individual field within a farm"""
    
    farm = models.ForeignKey(
        Farm,
        on_delete=models.CASCADE,
        related_name='fields'
    )
    field_name = models.CharField(max_length=FIELD_NAME_MAX_LENGTH)
    field_type = models.CharField(
        max_length=PHONE_MAX_LENGTH,
        choices=FIELD_TYPE_CHOICES
    )
    
    
    crop_type = models.CharField(
        max_length=100,
        blank=True,
        choices=CROP_TYPE_CHOICES,
        help_text='Type of crop grown'
    )
    crop_subtype = models.CharField(
        max_length=100,
        blank=True,
        choices=CROP_SUBTYPE_CHOICES,
        help_text='Specific crop subtype'
    )
    crop_subtype_other = models.CharField(
        max_length=200,
        blank=True,
        help_text='Specify other crop type'
    )
    small_grain_type = models.CharField(
        max_length=200,
        blank=True,
        help_text='Specify small grain type'
    )
    tillage_methods = models.CharField(
        max_length=TILLAGE_METHODS_MAX_LENGTH,
        blank=True,
        verbose_name='Tillage Methods',
        help_text='Tillage = any type of mechanical disturbance of the soil (e.g., disk, shanks, basket weed, broad fork, harrow, etc.)'
    )
    orchard_crop_specify = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Specify',
        help_text='Specify the type of fruit or nut trees'
    )
    
    forage_varieties = models.CharField(
        max_length=FORAGE_VARIETIES_MAX_LENGTH,
        blank=True,
        help_text='For rangeland'
    )
    paddock_size = models.CharField(
        max_length=PADDOCK_SIZE_MAX_LENGTH,
        blank=True,
        verbose_name='Paddock size (acres)',
        help_text='For rangeland'
    )
    pasture_size = models.CharField(
        max_length=PADDOCK_SIZE_MAX_LENGTH,
        blank=True,
        verbose_name='Pasture size (acres)',
        help_text='For rangeland - total pasture size in acres'
    )
    rootstock_species = models.CharField(
        max_length=ROOTSTOCK_SPECIES_MAX_LENGTH,
        blank=True,
        help_text='For orchards'
    )
    crop_varieties = models.CharField(
        max_length=CROP_VARIETIES_MAX_LENGTH,
        blank=True,
        help_text='Crop variety or varieties grown (for orchards)'
    )
    transitional_status = models.CharField(
        max_length=PHONE_MAX_LENGTH,
        choices=TRANSITIONAL_STATUS_CHOICES,
        blank=True,
        help_text='For orchards'
    )
    
    acres_sampled = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(ACRES_SAMPLED_MIN), MaxValueValidator(ACRES_SAMPLED_MAX)],
        verbose_name='Acres sampled',
        help_text='Total acres sampled for this field'
    )
    years_under_management = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(YEARS_UNDER_MANAGEMENT_MIN), MaxValueValidator(YEARS_UNDER_MANAGEMENT_MAX)],
        verbose_name='Number of years under current type of management',
        help_text='Years this field has been under current management'
    )
    supports_dairy = models.BooleanField(
        default=False,
        help_text='Does this field support dairy operations?'
    )
    is_confined_dairy = models.BooleanField(
        default=False,
        help_text='Is this a confined dairy operation?'
    )
    measurement_comments = models.TextField(
        blank=True,
        verbose_name='Field comments',
        help_text='General comments about the field'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Field')
        verbose_name_plural = _('Fields')
        constraints = [
            models.UniqueConstraint(
                fields=['farm', 'field_name'],
                name='unique_farm_field_name'
            )
        ]
        permissions = [
            ('manage_fields', 'Can manage fields'),
        ]
        ordering = ['farm', 'field_name']
    
    def __str__(self):
        return f"{self.farm.name} - {self.field_name}"


class ManagementPractices(models.Model):
    """Management practices for a specific field - persistent field-level practices"""
    
    field = models.OneToOneField(
        Field,
        on_delete=models.CASCADE,
        related_name='practices'
    )
    
    uses_tillage = models.BooleanField(default=False)
    tillage_depth = models.CharField(max_length=TILLAGE_DEPTH_MAX_LENGTH, blank=True)
    
    uses_cover_crop = models.BooleanField(default=False)
    cover_crop_termination = models.CharField(
        max_length=COVER_CROP_TERMINATION_MAX_LENGTH,
        blank=True,
        choices=COVER_CROP_TERMINATION_CHOICES,
        help_text='Method used to terminate cover crops'
    )
    cover_crop_termination_other = models.CharField(
        max_length=200,
        blank=True,
        help_text='Specify other termination method'
    )
    
    uses_synthetic_fertilizers = models.BooleanField(default=False)
    uses_synthetic_insecticides = models.BooleanField(
        default=False,
        verbose_name='Synthetic Insecticides or insecticide treated seed?'
    )
    uses_synthetic_herbicides = models.BooleanField(default=False)
    uses_synthetic_fungicides = models.BooleanField(
        default=False,
        verbose_name='Synthetic Fungicides or fungicide treated seed?'
    )
    
    uses_organic_amendments = models.BooleanField(default=False)
    organic_amendment_types = models.CharField(
        max_length=ORGANIC_AMENDMENT_TYPES_MAX_LENGTH,
        blank=True,
        choices=ORGANIC_AMENDMENT_CHOICES,
        verbose_name='Organic Amendment Types',
        help_text='Type of organic amendments used'
    )
    organic_amendment_other = models.CharField(
        max_length=200,
        blank=True,
        help_text='Specify other organic amendment type'
    )
    
    grazed_current_year = models.BooleanField(default=False, help_text='Grazed in current year')
    grazed_by_livestock_plan = models.BooleanField(
        default=False,
        verbose_name='Grazed by livestock as part of typical management plan',
        help_text='Grazed by livestock as part of typical management plan'
    )
    not_grazed_comments = models.TextField(blank=True, null=True, help_text='If not grazed in current year, explain')
    uses_grazing = models.BooleanField(default=False)
    grazer_types = models.CharField(
        max_length=GRAZER_TYPES_MAX_LENGTH,
        blank=True,
        choices=GRAZER_TYPES_CHOICES,
        help_text='Type of animals used for grazing'
    )
    grazer_types_other = models.CharField(
        max_length=200,
        blank=True,
        help_text='Specify other grazer type'
    )
    applies_insecticides_dewormers = models.BooleanField(default=False)
    
    insecticide_dewormer_frequency = models.CharField(
        max_length=INSECTICIDE_FREQUENCY_MAX_LENGTH,
        choices=INSECTICIDE_FREQUENCY_CHOICES,
        blank=True,
        help_text='Frequency of insecticide/dewormer application'
    )
    insecticide_dewormer_comments = models.TextField(
        blank=True,
        help_text='Timing details, name of insecticide/dewormer'
    )
    
    allows_ground_cover = models.BooleanField(default=False)
    ground_cover_management = models.CharField(
        max_length=GROUND_COVER_MANAGEMENT_MAX_LENGTH,
        blank=True,
        choices=GROUND_COVER_MANAGEMENT_CHOICES,
        help_text='Method used to manage ground cover'
    )
    ground_cover_management_other = models.CharField(
        max_length=200,
        blank=True,
        help_text='Specify other ground cover management method'
    )
    tills_between_rows = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Management Practices')
        verbose_name_plural = _('Management Practices')
    
    def __str__(self):
        return f"Management for {self.field.field_name}"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.grazed_current_year is False:
            if not (self.not_grazed_comments or '').strip():
                raise ValidationError({'not_grazed_comments': 'Please explain why the field was not grazed in the current year.'})


class TransectCode(models.Model):
    """Unique transect codes for validation - generated by administrators"""
    
    transect_code = models.CharField(max_length=TRANSECT_CODE_MAX_LENGTH, unique=True)
    is_active = models.BooleanField(default=True)
    is_used = models.BooleanField(default=False)
    used_in_application = models.ForeignKey(
        'GrowerApplication',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='used_transect_codes'
    )
    used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = _('Transect Code')
        verbose_name_plural = _('Transect Codes')
        permissions = [
            ('generate_transect_codes', 'Can generate transect codes'),
        ]
        ordering = ['transect_code']
    
    def __str__(self):
        return self.transect_code


class GrowerApplication(models.Model):
    submission_code = models.CharField(max_length=SUBMISSION_CODE_MAX_LENGTH, unique=True)
    field = models.ForeignKey(
        Field,
        on_delete=models.CASCADE,
        related_name='applications'
    )
    grower = models.ForeignKey(User, on_delete=models.CASCADE)
    
    is_draft = models.BooleanField(default=True)
    is_submitted = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(null=True, blank=True)
    date_sampled = models.DateField(help_text='Date when samples were collected', null=True, blank=True)
    grazing_start_date = models.DateField(null=True, blank=True, help_text='Start date (estimate) when grazing events began')
    
    transect_code_1 = models.CharField(max_length=TRANSECT_CODE_MAX_LENGTH, blank=True, null=True)
    transect_code_2 = models.CharField(max_length=TRANSECT_CODE_MAX_LENGTH, blank=True, null=True)
    transect_code_3 = models.CharField(max_length=TRANSECT_CODE_MAX_LENGTH, blank=True, null=True)
    transect_code_4 = models.CharField(max_length=TRANSECT_CODE_MAX_LENGTH, blank=True, null=True)
    
    # Transect coordinates
    transect_1_latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        help_text='Transect 1 latitude'
    )
    transect_1_longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        help_text='Transect 1 longitude'
    )
    transect_2_latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        help_text='Transect 2 latitude'
    )
    transect_2_longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        help_text='Transect 2 longitude'
    )
    transect_3_latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        help_text='Transect 3 latitude'
    )
    transect_3_longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        help_text='Transect 3 longitude'
    )
    transect_4_latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        help_text='Transect 4 latitude'
    )
    transect_4_longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        help_text='Transect 4 longitude'
    )
    
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Grower Application')
        verbose_name_plural = _('Grower Applications')
        constraints = [
            models.UniqueConstraint(
                fields=['field', 'date_sampled'],
                name='unique_field_date_sampled'
            )
        ]
        permissions = [
            ('manage_grower_applications', 'Can manage grower applications'),
        ]
        ordering = ['-date_sampled', '-created_at']
    
    @property
    def transect_codes(self):
        """Returns list of non-empty transect codes for this application"""
        codes = []
        for i in range(1, 5):
            char_field = getattr(self, f'transect_code_{i}', None)
            if char_field:
                codes.append(char_field)
        return codes
    
    @property
    def number_of_transects(self):
        return len(self.transect_codes)
    
    def clean(self):
        """Validate that at least one transect code is provided and all codes are valid"""
        from django.core.exceptions import ValidationError
        
        if self.is_submitted and self.is_draft:
            raise ValidationError('Application cannot be both draft and submitted.')
        
        if self.is_submitted:
            if not any([self.transect_code_1, self.transect_code_2, self.transect_code_3, self.transect_code_4]):
                raise ValidationError('At least one transect code is required.')
            
            for i in range(1, 5):
                char_field = getattr(self, f'transect_code_{i}', None)
                if char_field and char_field.strip():
                    try:
                        transect_obj = TransectCode.objects.get(transect_code=char_field.strip(), is_active=True)
                        if transect_obj.is_used:
                            raise ValidationError(f'Transect code {i} "{char_field}" has already been used in a submitted application.')
                    except TransectCode.DoesNotExist:
                        raise ValidationError(f'Transect code {i} "{char_field}" is not valid or inactive.')
    
    def save(self, *args, **kwargs):
        if not self.submission_code:
            if self.date_sampled:
                year_suffix = str(self.date_sampled.year)[-2:]
            else:
                year_suffix = str(timezone.now().year)[-2:]
            field_initials = ''.join([word[0] for word in self.field.field_name.split()]).upper()[:FIELD_INITIALS_MAX_LENGTH]
            grower_initials = self.grower.name[:GROWER_INITIALS_MAX_LENGTH].upper() if self.grower.name else GROWER_INITIALS_DEFAULT
            unique_suffix = str(uuid.uuid4()).split('-')[-1].upper()[:UUID_SUFFIX_LENGTH]
            self.submission_code = f"{SUBMISSION_CODE_PREFIX}-{year_suffix}-{field_initials}-{grower_initials}-{unique_suffix}"
        
        if self.is_submitted and not self.submitted_at:
            self.submitted_at = timezone.now()
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        date_display = self.date_sampled if self.date_sampled else 'No date'
        return f"{self.submission_code} - {self.field.field_name} ({date_display})"




class GrazingEvent(models.Model):
    """Grazing events for rangeland applications"""
    
    application = models.ForeignKey(
        GrowerApplication,
        on_delete=models.CASCADE,
        related_name='grazing_events'
    )
    event_number = models.IntegerField(
        validators=[MinValueValidator(GRAZING_EVENT_NUMBER_MIN), MaxValueValidator(GRAZING_EVENT_NUMBER_MAX)],
        help_text='1, 2, 3, or 4'
    )
    
    start_date = models.DateField(null=True, blank=True, help_text='Start date of grazing event')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Grazing Event')
        verbose_name_plural = _('Grazing Events')
        constraints = [
            models.UniqueConstraint(
                fields=['application', 'event_number'],
                name='unique_application_event_number'
            )
        ]
        ordering = ['application', 'event_number']
    
    def __str__(self):
        return f"Grazing Event {self.event_number} for {self.application}"


class GrazingEventAnimal(models.Model):
    """Individual animal entry within a grazing event"""
    
    grazing_event = models.ForeignKey(
        GrazingEvent,
        on_delete=models.CASCADE,
        related_name='animals'
    )
    class_of_animal = models.CharField(
        max_length=CLASS_OF_ANIMAL_MAX_LENGTH,
        help_text='e.g., Cow/calf pair, yearling cattle, ewe/lamb pair'
    )
    number_of_animals = models.IntegerField(
        validators=[MinValueValidator(NUMBER_OF_ANIMALS_MIN), MaxValueValidator(NUMBER_OF_ANIMALS_MAX)],
        help_text='Number of animals in this class'
    )
    average_weight_lbs = models.IntegerField(
        validators=[MinValueValidator(AVERAGE_WEIGHT_MIN), MaxValueValidator(AVERAGE_WEIGHT_MAX)],
        help_text='Average weight per animal in lbs'
    )
    duration_days = models.IntegerField(
        validators=[MinValueValidator(DURATION_DAYS_MIN), MaxValueValidator(DURATION_DAYS_MAX)],
        verbose_name='Grazing days',
        help_text='Grazing days'
    )
    rest_period_days = models.IntegerField(
        validators=[MinValueValidator(REST_PERIOD_DAYS_MIN), MaxValueValidator(REST_PERIOD_DAYS_MAX)],
        help_text='Rest period after grazing in days'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Grazing Event Animal'
        verbose_name_plural = 'Grazing Event Animals'
        ordering = ['id']
    
    def __str__(self):
        return f"{self.class_of_animal} - {self.number_of_animals} animals"


class CSVImportLog(models.Model):
    """Track CSV imports from administrators"""
    
    filename = models.CharField(max_length=CSV_FILENAME_MAX_LENGTH)
    imported_by = models.ForeignKey(User, on_delete=models.CASCADE)
    import_date = models.DateTimeField(auto_now_add=True)
    total_records = models.IntegerField(default=0)
    successful_records = models.IntegerField(default=0)
    failed_records = models.IntegerField(default=0)
    status = models.CharField(
        max_length=STATUS_MAX_LENGTH,
        choices=CSV_IMPORT_STATUS_CHOICES,
        default='pending'
    )
    error_log = models.TextField(blank=True)
    
    class Meta:
        verbose_name = _('CSV Import Log')
        verbose_name_plural = _('CSV Import Logs')
        ordering = ['-import_date']
    
    def __str__(self):
        return f"CSV Import: {self.filename} - {self.status}"


class GrowerReport(models.Model):
    """Generated reports for growers"""
    
    application = models.ForeignKey(
        GrowerApplication,
        on_delete=models.CASCADE,
        related_name='reports'
    )
    report_file = models.FileField(upload_to='grower_reports/')
    generated_at = models.DateTimeField(auto_now_add=True)
    generated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    email_sent = models.BooleanField(default=False)
    email_sent_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = _('Grower Report')
        verbose_name_plural = _('Grower Reports')
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"Report for {self.application.submission_code}"



class TransectMeasurement(models.Model):
    application = models.ForeignKey(
        GrowerApplication,
        on_delete=models.CASCADE,
        related_name='transect_measurements'
    )
    transect_index = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(4)])
    transect_code = models.CharField(max_length=TRANSECT_CODE_MAX_LENGTH, blank=True)

    general_time = models.CharField(max_length=50, blank=True)
    temperature_c = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    wind_speed_ms = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    field_condition = models.CharField(max_length=20, choices=FIELD_CONDITION_CHOICES, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [('application', 'transect_index')]
        ordering = ['application', 'transect_index']

    def __str__(self):
        return f"Measurement A:{self.application_id} T{self.transect_index} ({self.transect_code})"


class DropPlateReading(models.Model):
    measurement = models.ForeignKey(TransectMeasurement, on_delete=models.CASCADE, related_name='drop_plate')
    distance_m = models.IntegerField()
    value = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    class Meta:
        ordering = ['distance_m']


class VegetationReading(models.Model):
    measurement = models.ForeignKey(TransectMeasurement, on_delete=models.CASCADE, related_name='vegetation')
    metric = models.CharField(max_length=50, choices=VEGETATION_METRIC_CHOICES)
    position_m = models.IntegerField()
    value = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    class Meta:
        ordering = ['metric', 'position_m']


class SoilReading(models.Model):
    measurement = models.ForeignKey(TransectMeasurement, on_delete=models.CASCADE, related_name='soil')
    metric = models.CharField(max_length=50, choices=SOIL_METRIC_CHOICES)
    position_m = models.IntegerField()
    value = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    class Meta:
        ordering = ['metric', 'position_m']


class SoilCompactionReading(models.Model):
    measurement = models.ForeignKey(TransectMeasurement, on_delete=models.CASCADE, related_name='compaction')
    position_m = models.IntegerField()
    max_value = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    score = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(2)])
    hp = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    class Meta:
        ordering = ['position_m']


class InfiltrometerReading(models.Model):
    measurement = models.ForeignKey(TransectMeasurement, on_delete=models.CASCADE, related_name='infiltrometer')
    time_mark = models.CharField(max_length=10)
    volume_ml = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ['time_mark']


class InfiltrationRingReading(models.Model):
    measurement = models.ForeignKey(TransectMeasurement, on_delete=models.CASCADE, related_name='infiltration_ring')
    pour_number = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(2)])
    start_depth_cm = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    infiltration_time_sec = models.IntegerField(null=True, blank=True)
    depth_after_15min_cm = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    change_in_depth_cm = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    class Meta:
        ordering = ['pour_number']