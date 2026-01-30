from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from ..constants import (
    CSV_FILENAME_MAX_LENGTH,
    CSV_IMPORT_STATUS_CHOICES,
    FIELD_NAME_MAX_LENGTH,
    FILE_PATH_MAX_LENGTH,
    STATUS_MAX_LENGTH,
)
from .sample_codes import SampleCode

User = get_user_model()


class CSVImportLog(models.Model):
    """Track CSV imports from administrators"""

    filename = models.CharField(max_length=CSV_FILENAME_MAX_LENGTH)
    imported_by = models.ForeignKey(User, on_delete=models.CASCADE)
    import_date = models.DateTimeField(auto_now_add=True)
    file_path = models.CharField(max_length=FILE_PATH_MAX_LENGTH)
    description = models.TextField(blank=True)
    total_records = models.IntegerField(default=0)
    successful_records = models.IntegerField(default=0)
    failed_records = models.IntegerField(default=0)
    status = models.CharField(
        max_length=STATUS_MAX_LENGTH,
        choices=CSV_IMPORT_STATUS_CHOICES,
        default='pending'
    )
    error_log = models.JSONField(default=list, blank=True)

    class Meta:
        verbose_name = _('CSV Import Log')
        verbose_name_plural = _('CSV Import Logs')
        ordering = ['-import_date']

    def __str__(self):
        return f"CSV Import: {self.filename} - {self.status}"


class CSVImportFieldValue(models.Model):
    """Track CSV imports field values"""

    field_name = models.CharField(max_length=FIELD_NAME_MAX_LENGTH)
    field_value = models.CharField(max_length=255)
    row_number = models.IntegerField(null=True, blank=True)
    sample_code = models.ForeignKey(
        SampleCode,
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
        verbose_name = _('CSV Import Field Value')
        verbose_name_plural = _('CSV Import Field Value')
        ordering = ['import_log', 'sample_code', 'field_name']
