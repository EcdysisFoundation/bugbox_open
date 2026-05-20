from django.contrib import admin

from .models import BirdRecordingUpload


@admin.register(BirdRecordingUpload)
class BirdRecordingUploadAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'grower',
        'sample_code',
        'year_sampled',
        'original_filename',
        'file_size_bytes',
        'status',
        'uploaded_at',
        'created_at',
    )
    list_filter = ('status', 'year_sampled')
    search_fields = ('grower__email', 'sample_code__code', 'original_filename', 's3_key')
    readonly_fields = (
        'grower',
        'sample_code',
        'year_sampled',
        's3_key',
        'original_filename',
        'content_type',
        'file_size_bytes',
        'status',
        'uploaded_at',
        'created_at',
    )
    ordering = ('-created_at',)
