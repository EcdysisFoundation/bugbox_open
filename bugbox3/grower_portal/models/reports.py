from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from ..constants import (
    CLUSTER_NUMBER_MAX_LENGTH,
    LABEL_CATEGORY_CHOICES,
    LABEL_DESCRIPTION_MAX_LENGTH,
    LABEL_PROJECT_CHOICES,
)
from .application import GrowerApplication

User = get_user_model()


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


class LabelGeneration(models.Model):
    """Track label generation history for admin users"""

    project_type = models.CharField(
        max_length=20,
        choices=LABEL_PROJECT_CHOICES,
        help_text='Project type (Avalanche or 1000 Farms)'
    )
    label_category = models.CharField(
        max_length=20,
        choices=LABEL_CATEGORY_CHOICES,
        help_text='Label category (Inner or Outer)'
    )
    cluster_number = models.CharField(
        max_length=CLUSTER_NUMBER_MAX_LENGTH,
        help_text='Cluster number (e.g., C1, C2)'
    )
    year = models.IntegerField(help_text='Year for the labels')
    sample_types = models.JSONField(
        help_text='List of selected sample types'
    )
    labels_per_type = models.IntegerField(
        help_text='Number of labels generated per sample type'
    )
    total_labels_generated = models.IntegerField(
        help_text='Total number of labels in the document'
    )
    generated_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='label_generations'
    )
    generated_at = models.DateTimeField(auto_now_add=True)
    label_file = models.FileField(
        upload_to='label_documents/',
        help_text='Generated Word document with labels'
    )
    description = models.TextField(
        max_length=LABEL_DESCRIPTION_MAX_LENGTH,
        blank=True,
        help_text='Optional description or notes'
    )
    transect_codes_generated = models.JSONField(
        help_text='List of transect codes generated for this batch'
    )

    class Meta:
        verbose_name = _('Label Generation')
        verbose_name_plural = _('Label Generations')
        ordering = ['-generated_at']
        permissions = [
            ('generate_labels', 'Can generate labels'),
        ]

    def __str__(self):
        return f"{self.project_type} - {self.cluster_number} - {self.year} ({self.total_labels_generated} labels)"
