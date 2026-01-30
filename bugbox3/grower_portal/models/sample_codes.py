from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from ..constants import CLUSTER_NUMBER_MAX_LENGTH, LABEL_PROJECT_CHOICES

User = get_user_model()


class SampleCode(models.Model):
    """
    Project-agnostic code model supporting both Avalanche and Ignite projects.
    """
    code = models.CharField(
        max_length=20,
        unique=True,
        help_text='Unique code (transect code for Avalanche, site code for Ignite)')
    project_type = models.CharField(
        max_length=20,
        choices=LABEL_PROJECT_CHOICES,
        default='avalanche',
        help_text='Project type: Avalanche or Ignite'
    )
    cluster_number = models.CharField(
        max_length=CLUSTER_NUMBER_MAX_LENGTH,
        blank=True,
        default='',
        help_text='Cluster identifier')
    year = models.IntegerField(null=True, blank=True, help_text='Year for the labels')

    site_code_numeric = models.IntegerField(
        null=True,
        blank=True,
        help_text='Numeric site code for Ignite project (e.g., 5001)'
    )

    is_active = models.BooleanField(default=True)
    is_used = models.BooleanField(default=False)
    used_in_application = models.ForeignKey(
        'GrowerApplication',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='used_sample_codes'
    )
    used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('Sample Code')
        verbose_name_plural = _('Sample Codes')
        permissions = [
            ('generate_sample_codes', 'Can generate sample codes'),
        ]
        ordering = ['code']

    def __str__(self):
        return self.code


class SiteTransect(models.Model):
    """
    Transects for Ignite site codes (T1-T4), each site code can have up to 4 transects(1-4).
    """
    site_code = models.ForeignKey(
        SampleCode,
        on_delete=models.CASCADE,
        related_name='transects',
        help_text='Parent site code'
    )
    transect_number = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(4)],
        help_text='Transect number (1-4)'
    )
    is_active = models.BooleanField(default=True)
    is_used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _('Site Transect')
        verbose_name_plural = _('Site Transects')
        unique_together = [['site_code', 'transect_number']]
        ordering = ['site_code', 'transect_number']

    def __str__(self):
        return f"{self.site_code.code} T{self.transect_number}"


class GrowerSampleCodeMapping(models.Model):
    """Mapping between growers & sample codes"""
    grower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sample_code_mappings'
    )
    sample_code = models.ForeignKey(
        SampleCode,
        on_delete=models.CASCADE,
        related_name='grower_mappings'
    )
    year_sampled = models.IntegerField(
        help_text='Year the sample was taken (comes from application date_sampled).'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [['grower', 'sample_code']]
        verbose_name = _('Grower Sample Code Mapping')
        verbose_name_plural = _('Grower Sample Code Mappings')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.grower.email} - {self.sample_code.code}"
