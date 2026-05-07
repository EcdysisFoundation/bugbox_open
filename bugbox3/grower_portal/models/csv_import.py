from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from ..constants import (
    CATEGORY_CHOICES,
    CATEGORY_MAX_LENGTH,
    CSV_FILENAME_MAX_LENGTH,
    CSV_IMPORT_STATUS_CHOICES,
    FIELD_NAME_MAX_LENGTH,
    FILE_PATH_MAX_LENGTH,
    LABEL_PROJECT_CHOICES,
    RESULT_TYPE_CHOICES,
    STATUS_MAX_LENGTH,
)
from .sample_codes import SampleCode, SiteTransect

User = get_user_model()


class CSVImportLog(models.Model):
    """Track CSV imports from administrators"""

    filename = models.CharField(max_length=CSV_FILENAME_MAX_LENGTH)
    imported_by = models.ForeignKey(User, on_delete=models.CASCADE)
    import_date = models.DateTimeField(auto_now_add=True)
    file_path = models.CharField(max_length=FILE_PATH_MAX_LENGTH)
    description = models.TextField(blank=True)
    ingestion_metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text='Internal ingestion data (e.g. birds family_map). Not for admin-facing copy.',
    )
    total_records = models.IntegerField(default=0)
    successful_records = models.IntegerField(default=0)
    failed_records = models.IntegerField(default=0)
    status = models.CharField(
        max_length=STATUS_MAX_LENGTH,
        choices=CSV_IMPORT_STATUS_CHOICES,
        default='pending'
    )
    error_log = models.JSONField(default=list, blank=True)
    project_type = models.CharField(max_length=20, choices=LABEL_PROJECT_CHOICES, default='avalanche')
    result_type = models.CharField(max_length=20, choices=RESULT_TYPE_CHOICES, default='basic')
    category = models.CharField(
        max_length=CATEGORY_MAX_LENGTH,
        choices=CATEGORY_CHOICES,
        default='soils',
    )

    class Meta:
        verbose_name = _('CSV Import Log')
        verbose_name_plural = _('CSV Import Logs')
        ordering = ['-import_date']

    def __str__(self):
        return f"CSV Import: {self.filename} - {self.status}"


class CSVImportRow(models.Model):
    """Track CSV imports field rows"""
    row_number = models.IntegerField(null=True, blank=True)
    depth = models.CharField(max_length=255, null=True)
    sample_code = models.ForeignKey(
        SampleCode,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    site_transect = models.ForeignKey(
        SiteTransect,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    import_log = models.ForeignKey(
        CSVImportLog,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = _('CSV Import Row ')
        verbose_name_plural = _('CSV Import Row')
        ordering = ['import_log', 'sample_code', 'site_transect', 'depth']


class CSVImportFieldValue(models.Model):
    """Track CSV imports field values"""
    field_name = models.CharField(max_length=FIELD_NAME_MAX_LENGTH)
    field_value = models.CharField(max_length=255)
    row = models.ForeignKey(
        CSVImportRow,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = _('CSV Import Field Value')
        verbose_name_plural = _('CSV Import Field Value')
        ordering = ['row', 'field_name', 'field_value']
