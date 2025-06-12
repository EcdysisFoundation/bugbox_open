from django.contrib import admin
from .models import GBIFImageRecord, FilteredGBIFImageRecord

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


@admin.register(FilteredGBIFImageRecord)
class FilteredGBIFImageRecordAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'gbif_taxon_key',
        'canonical_name',
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
    search_fields = ('canonical_name', 'gbif_taxon_key', 'occurrence_id')
    list_filter = ('downloaded_image', 'media_type')
