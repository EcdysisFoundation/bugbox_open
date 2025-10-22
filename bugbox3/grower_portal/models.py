from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import uuid

from .constants import (
    GENDER_CHOICES, RACE_CHOICES, FIELD_TYPE_CHOICES,
    TRANSITIONAL_STATUS_CHOICES, INSECTICIDE_FREQUENCY_CHOICES,
    CSV_IMPORT_STATUS_CHOICES,
    AGE_MIN, AGE_MAX, LATITUDE_MIN, LATITUDE_MAX,
    LONGITUDE_MIN, LONGITUDE_MAX, GRAZING_EVENT_NUMBER_MIN,
    GRAZING_EVENT_NUMBER_MAX, REST_PERIOD_DAYS_MIN,
    REST_PERIOD_DAYS_MAX, NUMBER_OF_ANIMALS_MIN,
    NUMBER_OF_ANIMALS_MAX, AVERAGE_WEIGHT_MIN,
    AVERAGE_WEIGHT_MAX, DURATION_DAYS_MIN, DURATION_DAYS_MAX,
    PHONE_MAX_LENGTH, FARM_NAME_MAX_LENGTH, FIELD_NAME_MAX_LENGTH,
    CROP_VARIETY_MAX_LENGTH, FORAGE_VARIETIES_MAX_LENGTH,
    PADDOCK_SIZE_MAX_LENGTH, ROOTSTOCK_SPECIES_MAX_LENGTH,
    TILLAGE_DEPTH_MAX_LENGTH, COVER_CROP_TERMINATION_MAX_LENGTH,
    ORGANIC_AMENDMENT_TYPES_MAX_LENGTH, GRAZER_TYPES_MAX_LENGTH,
    INSECTICIDE_FREQUENCY_MAX_LENGTH, INSECTICIDE_COMMENTS_MAX_LENGTH,
    GROUND_COVER_MANAGEMENT_MAX_LENGTH, TRANSECT_CODE_MAX_LENGTH,
    SUBMISSION_CODE_MAX_LENGTH, CLASS_OF_ANIMAL_MAX_LENGTH,
    CSV_FILENAME_MAX_LENGTH, STATUS_MAX_LENGTH, SUBMISSION_CODE_PREFIX,
    FIELD_INITIALS_MAX_LENGTH, GROWER_INITIALS_MAX_LENGTH,
    GROWER_INITIALS_DEFAULT, UUID_SUFFIX_LENGTH,
    TRANSECT_NUMBER_MIN, TRANSECT_NUMBER_MAX,
    ACRES_SAMPLED_MIN, ACRES_SAMPLED_MAX,
    YEARS_UNDER_MANAGEMENT_MIN, YEARS_UNDER_MANAGEMENT_MAX
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
        unique_together = [['grower', 'name']]
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
    
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(LATITUDE_MIN), MaxValueValidator(LATITUDE_MAX)],
        help_text='Field latitude (-90 to 90)'
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(LONGITUDE_MIN), MaxValueValidator(LONGITUDE_MAX)],
        help_text='Field longitude (-180 to 180)'
    )
    
    crop_variety = models.CharField(
        max_length=CROP_VARIETY_MAX_LENGTH,
        blank=True,
        help_text='For crop fields and orchards'
    )
    forage_varieties = models.CharField(
        max_length=FORAGE_VARIETIES_MAX_LENGTH,
        blank=True,
        help_text='For rangeland'
    )
    paddock_size = models.CharField(
        max_length=PADDOCK_SIZE_MAX_LENGTH,
        blank=True,
        help_text='For rangeland'
    )
    rootstock_species = models.CharField(
        max_length=ROOTSTOCK_SPECIES_MAX_LENGTH,
        blank=True,
        help_text='For orchards'
    )
    transitional_status = models.CharField(
        max_length=PHONE_MAX_LENGTH,
        choices=TRANSITIONAL_STATUS_CHOICES,
        blank=True,
        help_text='For orchards'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Field')
        verbose_name_plural = _('Fields')
        unique_together = [['farm', 'field_name']]
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
        help_text='e.g., Grazing, Tillage, Other'
    )
    
    uses_synthetic_fertilizers = models.BooleanField(default=False)
    uses_synthetic_insecticides = models.BooleanField(default=False)
    uses_synthetic_herbicides = models.BooleanField(default=False)
    uses_synthetic_fungicides = models.BooleanField(default=False)
    
    uses_organic_amendments = models.BooleanField(default=False)
    organic_amendment_types = models.CharField(
        max_length=ORGANIC_AMENDMENT_TYPES_MAX_LENGTH,
        blank=True,
        help_text='e.g., Manure, Compost, Compost Tea, Organic Fertilizer'
    )
    
    uses_grazing = models.BooleanField(default=False)
    grazer_types = models.CharField(
        max_length=GRAZER_TYPES_MAX_LENGTH,
        blank=True,
        help_text='e.g., Chickens, Livestock'
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
        help_text='e.g., Tilling, Herbicide, Other'
    )
    tills_between_rows = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Management Practices')
        verbose_name_plural = _('Management Practices')
    
    def __str__(self):
        return f"Management for {self.field.field_name}"


class TransectCode(models.Model):
    """Unique transect codes for validation - generated by administrators"""
    
    transect_code = models.CharField(max_length=TRANSECT_CODE_MAX_LENGTH, unique=True)
    is_active = models.BooleanField(default=True)
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
    
    transect_code_1 = models.CharField(max_length=TRANSECT_CODE_MAX_LENGTH, blank=True, null=True)
    transect_code_2 = models.CharField(max_length=TRANSECT_CODE_MAX_LENGTH, blank=True, null=True)
    transect_code_3 = models.CharField(max_length=TRANSECT_CODE_MAX_LENGTH, blank=True, null=True)
    transect_code_4 = models.CharField(max_length=TRANSECT_CODE_MAX_LENGTH, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Grower Application')
        verbose_name_plural = _('Grower Applications')
        unique_together = [['field', 'date_sampled']]
        permissions = [
            ('manage_grower_applications', 'Can manage grower applications'),
        ]
        ordering = ['-date_sampled', '-created_at']
    
    @property
    def transect_codes(self):
        """Returns list of non-empty transect codes for this application"""
        codes = []
        if self.transect_code_1:
            codes.append(self.transect_code_1)
        if self.transect_code_2:
            codes.append(self.transect_code_2)
        if self.transect_code_3:
            codes.append(self.transect_code_3)
        if self.transect_code_4:
            codes.append(self.transect_code_4)
        return codes
    
    @property
    def number_of_transects(self):
        return len(self.transect_codes)
    
    def save(self, *args, **kwargs):
        if not self.submission_code:
            year_suffix = str(self.date_sampled.year)[-2:]
            field_initials = ''.join([word[0] for word in self.field.field_name.split()]).upper()[:FIELD_INITIALS_MAX_LENGTH]
            grower_initials = self.grower.name[:GROWER_INITIALS_MAX_LENGTH].upper() if self.grower.name else GROWER_INITIALS_DEFAULT
            unique_suffix = str(uuid.uuid4()).split('-')[-1].upper()[:UUID_SUFFIX_LENGTH]
            self.submission_code = f"{SUBMISSION_CODE_PREFIX}-{year_suffix}-{field_initials}-{grower_initials}-{unique_suffix}"
        
        if self.is_submitted and not self.submitted_at:
            self.submitted_at = timezone.now()
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.submission_code} - {self.field.field_name} ({self.date_sampled})"


class ApplicationMeasurement(models.Model):
    """Measurement data for each transect within an application"""
    
    application = models.ForeignKey(
        GrowerApplication,
        on_delete=models.CASCADE,
        related_name='measurements'
    )
    transect_number = models.IntegerField(
        validators=[MinValueValidator(TRANSECT_NUMBER_MIN), MaxValueValidator(TRANSECT_NUMBER_MAX)],
        help_text='1-4 within application (corresponds to application\'s transect codes)'
    )
    
    acres_sampled = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(ACRES_SAMPLED_MIN), MaxValueValidator(ACRES_SAMPLED_MAX)]
    )
    years_under_management = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(YEARS_UNDER_MANAGEMENT_MIN), MaxValueValidator(YEARS_UNDER_MANAGEMENT_MAX)]
    )
    
    supports_dairy = models.BooleanField(default=False)
    is_confined_dairy = models.BooleanField(
        default=False,
        help_text='For crop fields'
    )
    
    transect_latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(LATITUDE_MIN), MaxValueValidator(LATITUDE_MAX)],
        help_text='Transect latitude (-90 to 90) - specific location where this transect was sampled'
    )
    transect_longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(LONGITUDE_MIN), MaxValueValidator(LONGITUDE_MAX)],
        help_text='Transect longitude (-180 to 180) - specific location where this transect was sampled'
    )
    
    comments = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Application Measurement')
        verbose_name_plural = _('Application Measurements')
        unique_together = [['application', 'transect_number']]
        permissions = [
            ('view_application_measurements', 'Can view application measurements'),
            ('add_application_measurements', 'Can add application measurements'),
            ('change_application_measurements', 'Can change application measurements'),
            ('delete_application_measurements', 'Can delete application measurements'),
        ]
        ordering = ['application', 'transect_number']
    
    def __str__(self):
        transect_code = self.application.transect_codes[self.transect_number - 1] if self.transect_number <= len(self.application.transect_codes) else 'Unknown'
        return f"Measurement for Transect {self.transect_number} ({transect_code}) - {self.application.submission_code}"


class GrazingEvent(models.Model):
    """Grazing events for rangeland applications - measurement-specific events"""
    
    application_measurement = models.ForeignKey(
        ApplicationMeasurement,
        on_delete=models.CASCADE,
        related_name='grazing_events'
    )
    event_number = models.IntegerField(
        validators=[MinValueValidator(GRAZING_EVENT_NUMBER_MIN), MaxValueValidator(GRAZING_EVENT_NUMBER_MAX)],
        help_text='1, 2, 3, or 4'
    )
    rest_period_days = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(REST_PERIOD_DAYS_MIN), MaxValueValidator(REST_PERIOD_DAYS_MAX)],
        help_text='Rest period between grazing events in days'
    )
    class_of_animal = models.CharField(
        max_length=CLASS_OF_ANIMAL_MAX_LENGTH,
        help_text='e.g., Cow/calf pair, yearling cattle, ewe/lamb pair'
    )
    number_of_animals = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(NUMBER_OF_ANIMALS_MIN), MaxValueValidator(NUMBER_OF_ANIMALS_MAX)]
    )
    average_weight_lbs = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(AVERAGE_WEIGHT_MIN), MaxValueValidator(AVERAGE_WEIGHT_MAX)]
    )
    duration_days = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(DURATION_DAYS_MIN), MaxValueValidator(DURATION_DAYS_MAX)]
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Grazing Event')
        verbose_name_plural = _('Grazing Events')
        unique_together = [['application_measurement', 'event_number']]
        ordering = ['application_measurement', 'event_number']
    
    def __str__(self):
        return f"Grazing Event {self.event_number} for {self.application_measurement}"


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

