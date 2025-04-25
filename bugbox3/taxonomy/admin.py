from django.contrib import admin
from .models import GBIFImageRecord

@admin.register(GBIFImageRecord)
class GBIFImageRecordAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'gbif_taxon_key',
        'scientific_name',
        'image_url',
        'media_type',
        'license',
        'morphospecies',
        'date_fetched',
        'decimal_latitude',
        'decimal_longitude',
        'occurrence_id',
        'downloaded_image',
    )
    search_fields = ('scientific_name', 'gbif_taxon_key', 'occurrence_id')
    list_filter = ('downloaded_image', 'media_type')
