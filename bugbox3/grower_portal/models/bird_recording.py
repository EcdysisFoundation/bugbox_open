from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from .sample_codes import SampleCode

User = get_user_model()


class BirdRecordingUpload(models.Model):
    """Metadata for grower bird audio uploaded to S3."""

    STATUS_PENDING = 'pending'
    STATUS_COMPLETED = 'completed'
    STATUS_FAILED = 'failed'
    STATUS_CHOICES = [
        (STATUS_PENDING, _('Pending')),
        (STATUS_COMPLETED, _('Completed')),
        (STATUS_FAILED, _('Failed')),
    ]

    grower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='bird_recording_uploads',
    )
    sample_code = models.ForeignKey(
        SampleCode,
        on_delete=models.PROTECT,
        related_name='bird_recording_uploads',
    )
    year_sampled = models.IntegerField(
        help_text='Year for S3 path: mapping if present, else SampleCode.year, else current year.',
    )
    s3_key = models.CharField(max_length=512)
    original_filename = models.CharField(max_length=255)
    content_type = models.CharField(max_length=128)
    file_size_bytes = models.BigIntegerField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )
    uploaded_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Bird recording upload')
        verbose_name_plural = _('Bird recording uploads')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['grower', '-created_at']),
            models.Index(fields=['sample_code', '-created_at']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f'{self.sample_code.code} — {self.original_filename} ({self.status})'
