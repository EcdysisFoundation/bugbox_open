from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from ..constants import (
    ACRES_SAMPLED_MAX,
    ACRES_SAMPLED_MIN,
    CROP_SUBTYPE_CHOICES,
    CROP_TYPE_CHOICES,
    CROP_VARIETIES_MAX_LENGTH,
    FARM_NAME_MAX_LENGTH,
    FIELD_NAME_MAX_LENGTH,
    FIELD_TYPE_CHOICES,
    FORAGE_VARIETIES_MAX_LENGTH,
    PADDOCK_SIZE_MAX_LENGTH,
    PHONE_MAX_LENGTH,
    ROOTSTOCK_SPECIES_MAX_LENGTH,
    TILLAGE_METHODS_MAX_LENGTH,
    TRANSITIONAL_STATUS_CHOICES,
    YEARS_UNDER_MANAGEMENT_MAX,
    YEARS_UNDER_MANAGEMENT_MIN,
)

User = get_user_model()


class Farm(models.Model):
    """Farm/organization entity - one grower can have multiple farms"""
    grower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='farms',
        null=True,
        blank=True,
        help_text='Grower user account (optional for admin-created applications)'
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
                name='unique_grower_farm_name',
                nulls_distinct=True
            )
        ]
        permissions = [
            ('manage_farms', 'Can manage farms'),
        ]
        ordering = ['name']

    def __str__(self):
        if self.grower:
            return f"{self.name} ({self.grower.name})"
        return f"{self.name} (No linked account)"


class Field(models.Model):
    """Individual field within a farm"""

    farm = models.ForeignKey(
        Farm,
        on_delete=models.CASCADE,
        related_name='fields',
        help_text='Farm this field belongs to'
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
        help_text=(
            'Tillage = any type of mechanical disturbance of the soil '
            '(e.g., disk, shanks, basket weed, broad fork, harrow, etc.)'
        )
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
