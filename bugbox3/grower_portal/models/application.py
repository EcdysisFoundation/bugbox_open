import uuid

from django.contrib.auth import get_user_model
from django.contrib.gis.db.models import PointField
from django.contrib.gis.geos import Point
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from ..constants import (
    AVERAGE_WEIGHT_KG_MAX,
    AVERAGE_WEIGHT_KG_MIN,
    CLASS_OF_ANIMAL_MAX_LENGTH,
    COVER_CROP_TERMINATION_CHOICES,
    COVER_CROP_TERMINATION_MAX_LENGTH,
    DURATION_DAYS_MAX,
    DURATION_DAYS_MIN,
    FIELD_INITIALS_MAX_LENGTH,
    GRAZER_TYPES_CHOICES,
    GRAZER_TYPES_MAX_LENGTH,
    GRAZING_EVENT_NUMBER_MAX,
    GRAZING_EVENT_NUMBER_MIN,
    GROUND_COVER_MANAGEMENT_CHOICES,
    GROUND_COVER_MANAGEMENT_MAX_LENGTH,
    GROWER_INITIALS_DEFAULT,
    GROWER_INITIALS_MAX_LENGTH,
    INSECTICIDE_FREQUENCY_CHOICES,
    INSECTICIDE_FREQUENCY_MAX_LENGTH,
    NUMBER_OF_ANIMALS_MAX,
    NUMBER_OF_ANIMALS_MIN,
    ORGANIC_AMENDMENT_CHOICES,
    ORGANIC_AMENDMENT_TYPES_MAX_LENGTH,
    PHONE_MAX_LENGTH,
    REST_PERIOD_DAYS_MAX,
    REST_PERIOD_DAYS_MIN,
    DEFAULT_DEPTH_UNIT,
    DEFAULT_TIME_UNIT,
    DEFAULT_WEIGHT_UNIT,
    DEPTH_UNIT_CHOICES,
    SUBMISSION_CODE_MAX_LENGTH,
    SUBMISSION_CODE_PREFIX,
    TILLAGE_DEPTH_MAX_LENGTH,
    TIME_UNIT_CHOICES,
    TRANSECT_CODE_MAX_LENGTH,
    UUID_SUFFIX_LENGTH,
    WEIGHT_UNIT_CHOICES,
)
from .farm import Field
from .sample_codes import GrowerSampleCodeMapping, SampleCode

User = get_user_model()


class GrowerApplication(models.Model):
    submission_code = models.CharField(max_length=SUBMISSION_CODE_MAX_LENGTH, unique=True)
    field = models.ForeignKey(
        Field,
        on_delete=models.CASCADE,
        related_name='applications',
        null=True,
        blank=True,
        help_text='Field for this application (created in step 1)'
    )
    grower = models.ForeignKey(
        User,
        related_name="grower_applications",
        verbose_name="Grower",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text='Grower user account (optional if created by admin)'
    )

    grower_name = models.CharField(
        max_length=200,
        blank=True,
        help_text='Grower name when no user account exists'
    )
    grower_email = models.EmailField(
        blank=True,
        help_text='Grower email when no user account exists'
    )
    grower_phone = models.CharField(
        max_length=PHONE_MAX_LENGTH,
        blank=True,
        help_text='Grower phone when no user account exists'
    )

    created_by_admin = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='admin_created_applications',
        help_text='Admin user who created this application on behalf of grower'
    )
    is_admin_created = models.BooleanField(
        default=False,
        help_text='Whether this application was created by an admin'
    )

    is_draft = models.BooleanField(default=True)
    is_submitted = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(null=True, blank=True)
    date_sampled = models.DateField(help_text='Date when samples were collected', null=True, blank=True)
    grazing_start_date = models.DateField(
        null=True,
        blank=True,
        help_text='Start date (estimate) when grazing events began')

    transect_code_1 = models.CharField(max_length=TRANSECT_CODE_MAX_LENGTH, blank=True, null=True)
    transect_code_2 = models.CharField(max_length=TRANSECT_CODE_MAX_LENGTH, blank=True, null=True)
    transect_code_3 = models.CharField(max_length=TRANSECT_CODE_MAX_LENGTH, blank=True, null=True)
    transect_code_4 = models.CharField(max_length=TRANSECT_CODE_MAX_LENGTH, blank=True, null=True)

    transect_1_location = PointField(
        null=True,
        blank=True,
        srid=4326,
        help_text='Transect 1 GPS location (longitude, latitude)'
    )
    transect_2_location = PointField(
        null=True,
        blank=True,
        srid=4326,
        help_text='Transect 2 GPS location (longitude, latitude)'
    )
    transect_3_location = PointField(
        null=True,
        blank=True,
        srid=4326,
        help_text='Transect 3 GPS location (longitude, latitude)'
    )
    transect_4_location = PointField(
        null=True,
        blank=True,
        srid=4326,
        help_text='Transect 4 GPS location (longitude, latitude)'
    )

    def set_transect_location(self, transect_num, longitude, latitude):
        try:
            lng = float(longitude) if longitude not in (None, '') else None
            lat = float(latitude) if latitude not in (None, '') else None
        except (ValueError, TypeError):
            lng = None
            lat = None

        if lng is not None and lat is not None:
            point = Point(lng, lat, srid=4326)
            setattr(self, f'transect_{transect_num}_location', point)
        else:
            setattr(self, f'transect_{transect_num}_location', None)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Grower Application')
        verbose_name_plural = _('Grower Applications')
        constraints = [
            models.UniqueConstraint(
                fields=['field', 'date_sampled'],
                name='unique_field_date_sampled',
                nulls_distinct=True
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

        if self.is_submitted and self.is_draft:
            raise ValidationError('Application cannot be both draft and submitted.')

        if self.is_submitted:
            if not self.date_sampled:
                raise ValidationError(
                    {'date_sampled': 'Date sampled is required when submitting an application.'}
                )
            if not any([self.transect_code_1, self.transect_code_2, self.transect_code_3, self.transect_code_4]):
                raise ValidationError('At least one transect code is required.')

            for i in range(1, 5):
                char_field = getattr(self, f'transect_code_{i}', None)
                if char_field and char_field.strip():
                    try:
                        transect_obj = SampleCode.objects.get(code=char_field.strip(), is_active=True)
                        # allow codes already reserved for this application
                        if (
                            transect_obj.is_used
                            and transect_obj.used_in_application_id != self.pk
                        ):
                            other = transect_obj.used_in_application
                            scode = (
                                other.submission_code if other else 'another application'
                            )
                            raise ValidationError(
                                f'Transect code {i} "{char_field}" has already been used in application {scode}.'
                            )
                    except SampleCode.DoesNotExist:
                        raise ValidationError(f'Transect code {i} "{char_field}" is not valid or inactive.')

    def save(self, *args, **kwargs):
        previous = None
        if self.pk:
            try:
                previous = type(self).objects.only('is_submitted', 'grower_id').get(pk=self.pk)
            except type(self).DoesNotExist:
                previous = None

        was_submitted = previous.is_submitted if previous else False
        previous_grower_id = previous.grower_id if previous else None

        if not self.submission_code:
            if self.date_sampled:
                year_suffix = str(self.date_sampled.year)[-2:]
            else:
                year_suffix = str(timezone.now().year)[-2:]

            if self.field and self.field.field_name:
                field_initials = ''.join([word[0] for word in self.field.field_name.split()]
                                         ).upper()[:FIELD_INITIALS_MAX_LENGTH]
            else:
                field_initials = 'FLD'

            if self.grower and hasattr(self.grower, 'name') and self.grower.name:
                grower_initials = self.grower.name[:GROWER_INITIALS_MAX_LENGTH].upper()
            elif self.grower_name:
                grower_initials = self.grower_name[:GROWER_INITIALS_MAX_LENGTH].upper()
            else:
                grower_initials = GROWER_INITIALS_DEFAULT

            unique_suffix = str(uuid.uuid4()).split('-')[-1].upper()[:UUID_SUFFIX_LENGTH]
            self.submission_code = (
                f"{SUBMISSION_CODE_PREFIX}-{year_suffix}-{field_initials}-{grower_initials}-{unique_suffix}"
            )

        if self.is_submitted and not self.submitted_at:
            self.submitted_at = timezone.now()

        if self.created_by_admin is not None:
            self.is_admin_created = True

        if self.is_submitted:
            self.full_clean()

        super().save(*args, **kwargs)

        if self.is_submitted and self.grower_id and (not was_submitted or previous_grower_id != self.grower_id):
            self.ensure_grower_sample_code_mappings()

    def get_transect_sample_codes(self):
        sample_codes = []
        for i in range(1, 5):
            raw = getattr(self, f'transect_code_{i}', None)
            code = raw.strip() if isinstance(raw, str) else ''
            if not code:
                continue
            try:
                sample_codes.append(SampleCode.objects.get(code=code))
            except SampleCode.DoesNotExist:
                continue
        return sample_codes

    def ensure_grower_sample_code_mappings(self):
        if not self.grower_id or not self.date_sampled:
            return 0

        mapping_year = self.date_sampled.year
        created_count = 0
        for sample_code in self.get_transect_sample_codes():
            mapping, created = GrowerSampleCodeMapping.objects.get_or_create(
                grower_id=self.grower_id,
                sample_code=sample_code,
                defaults={'year_sampled': mapping_year},
            )
            if created:
                created_count += 1
            elif mapping.year_sampled != mapping_year:
                mapping.year_sampled = mapping_year
                mapping.save(update_fields=['year_sampled'])
        return created_count

    @property
    def grower_display_name(self):
        """Returns the grower's name from user account or grower_name field"""
        if self.grower:
            return self.grower.name if hasattr(self.grower, 'name') else self.grower.email
        return self.grower_name or 'Unknown Grower'

    @property
    def grower_display_email(self):
        """Returns the grower's email from user account or grower_email field"""
        if self.grower:
            return self.grower.email
        return self.grower_email or 'No email'

    @property
    def has_linked_account(self):
        """Returns True if this application is linked to a user account"""
        return self.grower is not None

    def __str__(self):
        date_display = self.date_sampled if self.date_sampled else 'No date'
        field_name = self.field.field_name if self.field else 'No field'
        return f"{self.submission_code} - {field_name} ({date_display})"


class ManagementPractices(models.Model):
    """Management practices for a specific application, practices for each sampling event"""

    application = models.ForeignKey(
        GrowerApplication,
        on_delete=models.CASCADE,
        related_name='management_practices'
    )

    uses_tillage = models.BooleanField(default=False)
    tillage_depth_cm = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Canonical tillage depth in centimeters for reporting',
    )
    tillage_depth_entered = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Tillage depth as entered by the grower',
    )
    tillage_depth_unit = models.CharField(
        max_length=10,
        choices=DEPTH_UNIT_CHOICES,
        default=DEFAULT_DEPTH_UNIT,
        blank=True,
        help_text='Unit used when entering tillage depth',
    )

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
        return f"Management for {self.application.submission_code}"

    def clean(self):
        if self.grazed_current_year is False:
            if not (self.not_grazed_comments or '').strip():
                raise ValidationError(
                    {'not_grazed_comments': 'Please explain why the field was not grazed in the current year.'})


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
    average_weight_kg = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(AVERAGE_WEIGHT_KG_MIN), MaxValueValidator(AVERAGE_WEIGHT_KG_MAX)],
        help_text='Average weight per animal in kg',
    )
    average_weight_entered = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Average weight as entered by the grower',
    )
    average_weight_unit = models.CharField(
        max_length=10,
        choices=WEIGHT_UNIT_CHOICES,
        default=DEFAULT_WEIGHT_UNIT,
        help_text='Unit used when entering average weight',
    )
    duration_days = models.IntegerField(
        validators=[MinValueValidator(DURATION_DAYS_MIN), MaxValueValidator(DURATION_DAYS_MAX)],
        verbose_name='Grazing days',
        help_text='Grazing days',
    )
    duration_entered = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Grazing duration as entered by the grower',
    )
    duration_unit = models.CharField(
        max_length=10,
        choices=TIME_UNIT_CHOICES,
        default=DEFAULT_TIME_UNIT,
        help_text='Unit used when entering grazing duration',
    )
    rest_period_days = models.IntegerField(
        validators=[MinValueValidator(REST_PERIOD_DAYS_MIN), MaxValueValidator(REST_PERIOD_DAYS_MAX)],
        help_text='Rest period after grazing in days',
    )
    rest_period_entered = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Rest period as entered by the grower',
    )
    rest_period_unit = models.CharField(
        max_length=10,
        choices=TIME_UNIT_CHOICES,
        default=DEFAULT_TIME_UNIT,
        help_text='Unit used when entering rest period',
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Grazing Event Animal'
        verbose_name_plural = 'Grazing Event Animals'
        ordering = ['id']

    def __str__(self):
        return f"{self.class_of_animal} - {self.number_of_animals} animals"
