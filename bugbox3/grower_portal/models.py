from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import pytz

User = get_user_model()


class GrowerProfile(models.Model):
    """
    Profile information for growers.
    This is completed during initial signup and can be edited later.
    """
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('prefer_not_to_say', 'Prefer not to say'),
    ]
    
    RACE_CHOICES = [
        ('american_indian_alaska_native', 'American Indian or Alaska Native'),
        ('asian', 'Asian'),
        ('black_african_american', 'Black or African American'),
        ('native_hawaiian_pacific_islander', 'Native Hawaiian or Other Pacific Islander'),
        ('white', 'White'),
        ('two_or_more_races', 'Two or More Races'),
        ('prefer_not_to_say', 'Prefer not to say'),
    ]
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='grower_profile'
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )
    gender = models.CharField(
        max_length=20,
        choices=GENDER_CHOICES,
        blank=True,
        null=True
    )
    age = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text='Age in years',
        validators=[MinValueValidator(1), MaxValueValidator(120)]
    )
    race = models.CharField(
        max_length=50,
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
    name = models.CharField(max_length=200)
    
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
    """Individual field within a farm - has persistent properties including GPS location"""
    
    FIELD_TYPE_CHOICES = [
        ('crop', 'Crop Field'),
        ('range', 'Rangeland/Pasture'),
        ('orchard', 'Orchard'),
    ]
    
    TRANSITIONAL_STATUS_CHOICES = [
        ('1st_year', '1st year'),
        ('2nd_year', '2nd year'),
        ('3rd_year', '3rd year'),
        ('4th_year', '4th year'),
    ]
    
    farm = models.ForeignKey(
        Farm,
        on_delete=models.CASCADE,
        related_name='fields'
    )
    field_name = models.CharField(max_length=200)
    field_type = models.CharField(
        max_length=20,
        choices=FIELD_TYPE_CHOICES
    )
    
    # GPS Coordinates - field location (selected via Google Maps integration)
    # These are fixed for a field since the physical location doesn't change
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
        help_text='Field latitude (-90 to 90)'
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
        help_text='Field longitude (-180 to 180)'
    )
    
    # Field-specific properties based on type
    crop_variety = models.CharField(
        max_length=200,
        blank=True,
        help_text='For crop fields and orchards'
    )
    forage_varieties = models.CharField(
        max_length=500,
        blank=True,
        help_text='For rangeland'
    )
    paddock_size = models.CharField(
        max_length=100,
        blank=True,
        help_text='For rangeland'
    )
    rootstock_species = models.CharField(
        max_length=500,
        blank=True,
        help_text='For orchards'
    )
    transitional_status = models.CharField(
        max_length=20,
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
    
    # Tillage practices
    uses_tillage = models.BooleanField(default=False)
    tillage_depth = models.CharField(max_length=50, blank=True)
    
    # Cover crops
    uses_cover_crop = models.BooleanField(default=False)
    cover_crop_termination = models.CharField(
        max_length=100,
        blank=True,
        help_text='e.g., Grazing, Tillage, Other'
    )
    
    # Synthetic inputs
    uses_synthetic_fertilizers = models.BooleanField(default=False)
    uses_synthetic_insecticides = models.BooleanField(default=False)
    uses_synthetic_herbicides = models.BooleanField(default=False)
    uses_synthetic_fungicides = models.BooleanField(default=False)
    
    # Organic amendments
    uses_organic_amendments = models.BooleanField(default=False)
    organic_amendment_types = models.CharField(
        max_length=500,
        blank=True,
        help_text='e.g., Manure, Compost, Compost Tea, Organic Fertilizer'
    )
    
    # Grazing practices (for rangeland/orchards)
    uses_grazing = models.BooleanField(default=False)
    grazer_types = models.CharField(
        max_length=200,
        blank=True,
        help_text='e.g., Chickens, Livestock'
    )
    applies_insecticides_dewormers = models.BooleanField(default=False)
    insecticide_dewormer_frequency = models.CharField(
        max_length=100,
        blank=True,
        help_text='e.g., Not used, Once per year, Multiple times per year'
    )
    
    # Orchard-specific practices
    allows_ground_cover = models.BooleanField(default=False)
    ground_cover_management = models.CharField(
        max_length=100,
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
    
    transect_code = models.CharField(max_length=20, unique=True)
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
    """
    Main application container - one per field per year/sampling period
    Transect codes are stored here (can vary per application for the same field)
    """
    
    submission_code = models.CharField(max_length=50, unique=True)
    field = models.ForeignKey(
        Field,
        on_delete=models.CASCADE,
        related_name='applications'
    )
    grower = models.ForeignKey(User, on_delete=models.CASCADE)
    
    is_draft = models.BooleanField(default=True)
    is_submitted = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(null=True, blank=True)
    application_year = models.IntegerField()
    
    # Transect Codes - specific to this application (can vary per year for same field)
    transect_code_1 = models.CharField(max_length=20, blank=True, null=True)
    transect_code_2 = models.CharField(max_length=20, blank=True, null=True)
    transect_code_3 = models.CharField(max_length=20, blank=True, null=True)
    transect_code_4 = models.CharField(max_length=20, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Grower Application')
        verbose_name_plural = _('Grower Applications')
        unique_together = [['field', 'application_year']]
        permissions = [
            ('manage_grower_applications', 'Can manage grower applications'),
        ]
        ordering = ['-application_year', '-created_at']
    
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
        """Dynamic property to get number of transects from this application"""
        return len(self.transect_codes)
    
    def save(self, *args, **kwargs):
        if not self.submission_code:
            # Generate a unique submission code
            year_suffix = str(self.application_year)[-2:]
            field_initials = ''.join([word[0] for word in self.field.field_name.split()]).upper()[:3]
            grower_initials = self.grower.name[:2].upper() if self.grower.name else 'GR'
            # Simple unique suffix
            count = GrowerApplication.objects.filter(application_year=self.application_year).count() + 1
            self.submission_code = f"APP-{year_suffix}-{field_initials}-{grower_initials}-{count:04d}"
        
        # Auto-capture submission timestamp in Brookings, SD timezone
        if self.is_submitted and not self.submitted_at:
            brookings_tz = pytz.timezone('America/Chicago')  # Brookings, SD is in Central Time
            self.submitted_at = timezone.now().astimezone(brookings_tz)
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.submission_code} - {self.field.field_name} ({self.application_year})"


class ApplicationMeasurement(models.Model):
    """
    Measurement data for each transect within an application
    GPS coordinates are from Field level (field location doesn't change)
    Transect codes are from Application level (can vary per application/year)
    This model stores the actual measurement data for each transect
    """
    
    application = models.ForeignKey(
        GrowerApplication,
        on_delete=models.CASCADE,
        related_name='measurements'
    )
    transect_number = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(4)],
        help_text='1-4 within application (corresponds to application\'s transect codes)'
    )
    
    # Sample specifications - actual measurement context
    acres_sampled = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0.1), MaxValueValidator(10000)]
    )
    years_under_management = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # Dairy operation context - measurement-specific
    supports_dairy = models.BooleanField(default=False)
    is_confined_dairy = models.BooleanField(
        default=False,
        help_text='For crop fields'
    )
    
    # Measurement-specific comments
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
    
    EVENT_TYPE_CHOICES = [
        ('start', 'Start Grazing'),
        ('end', 'End Grazing'),
        ('move', 'Move Animals'),
    ]
    
    application_measurement = models.ForeignKey(
        ApplicationMeasurement,
        on_delete=models.CASCADE,
        related_name='grazing_events'
    )
    event_number = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(4)],
        help_text='1, 2, 3, or 4'
    )
    rest_period_days = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(365)],
        help_text='Rest period between grazing events in days'
    )
    class_of_animal = models.CharField(
        max_length=100,
        help_text='e.g., Cow/calf pair, yearling cattle, ewe/lamb pair'
    )
    number_of_animals = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(10000)]
    )
    average_weight_lbs = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5000)]
    )
    duration_days = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(365)]
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
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    filename = models.CharField(max_length=255)
    imported_by = models.ForeignKey(User, on_delete=models.CASCADE)
    import_date = models.DateTimeField(auto_now_add=True)
    total_records = models.IntegerField(default=0)
    successful_records = models.IntegerField(default=0)
    failed_records = models.IntegerField(default=0)
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
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

