from django.contrib import admin
from .models import (
    GrowerProfile,
    Farm,
    Field,
    ManagementPractices,
    TransectCode,
    GrowerApplication,
    GrazingEvent,
    GrazingEventAnimal,
    CSVImportLog,
    GrowerReport,
    TransectMeasurement,
    DropPlateReading,
    VegetationReading,
    SoilReading,
    SoilCompactionReading,
    InfiltrometerReading,
    InfiltrationRingReading,
)


@admin.register(GrowerProfile)
class GrowerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'gender', 'age', 'profile_completed', 'created_at')
    list_filter = ('profile_completed', 'gender', 'race')
    search_fields = ('user__name', 'user__email', 'phone')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'profile_completed')
        }),
        ('Personal Information', {
            'fields': ('phone', 'gender', 'age', 'race')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Farm)
class FarmAdmin(admin.ModelAdmin):
    list_display = ('name', 'grower', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'grower__name', 'grower__email')
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ['grower']


@admin.register(Field)
class FieldAdmin(admin.ModelAdmin):
    list_display = ('field_name', 'farm', 'field_type', 'created_at')
    list_filter = ('field_type', 'transitional_status')
    search_fields = ('field_name', 'farm__name', 'farm__grower__name')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('farm', 'field_name', 'field_type')
        }),
        ('Field-Specific Properties', {
            'fields': (
                'crop_type',
                'crop_subtype',
                'crop_subtype_other',
                'small_grain_type',
                'tillage_methods',
                'forage_varieties',
                'paddock_size',
                'rootstock_species',
                'transitional_status',
                'orchard_crop_specify'
            ),
            'description': 'Fill in based on field type'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ManagementPractices)
class ManagementPracticesAdmin(admin.ModelAdmin):
    list_display = ('field', 'uses_tillage', 'uses_cover_crop', 'uses_grazing', 'created_at')
    list_filter = (
        'uses_tillage',
        'uses_cover_crop',
        'uses_synthetic_fertilizers',
        'uses_grazing'
    )
    search_fields = ('field__field_name', 'field__farm__name')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Field', {
            'fields': ('field',)
        }),
        ('Tillage Practices', {
            'fields': ('uses_tillage', 'tillage_depth')
        }),
        ('Cover Crops', {
            'fields': ('uses_cover_crop', 'cover_crop_termination')
        }),
        ('Synthetic Inputs', {
            'fields': (
                'uses_synthetic_fertilizers',
                'uses_synthetic_insecticides',
                'uses_synthetic_herbicides',
                'uses_synthetic_fungicides'
            )
        }),
        ('Organic Amendments', {
            'fields': ('uses_organic_amendments', 'organic_amendment_types')
        }),
        ('Grazing Practices', {
            'fields': (
                'uses_grazing',
                'grazer_types',
                'applies_insecticides_dewormers',
                'insecticide_dewormer_frequency'
            )
        }),
        ('Orchard-Specific', {
            'fields': (
                'allows_ground_cover',
                'ground_cover_management',
                'tills_between_rows'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(TransectCode)
class TransectCodeAdmin(admin.ModelAdmin):
    list_display = ('transect_code', 'is_active', 'is_used', 'used_in_application', 'created_by', 'created_at')
    list_filter = ('is_active', 'is_used', 'created_at')
    search_fields = ('transect_code', 'used_in_application__submission_code')
    readonly_fields = ('created_at', 'used_at')
    autocomplete_fields = ['created_by', 'used_in_application']
    fieldsets = (
        ('Code Information', {
            'fields': ('transect_code', 'is_active', 'created_by', 'created_at')
        }),
        ('Usage Tracking', {
            'fields': ('is_used', 'used_in_application', 'used_at'),
            'description': 'Tracks if this code has been used in a submitted application'
        }),
    )


@admin.register(GrowerApplication)
class GrowerApplicationAdmin(admin.ModelAdmin):
    list_display = (
        'submission_code',
        'field',
        'grower',
        'date_sampled',
        'number_of_transects',
        'is_draft',
        'is_submitted',
        'submitted_at'
    )
    list_filter = ('is_draft', 'is_submitted', 'date_sampled', 'field__field_type')
    search_fields = (
        'submission_code',
        'field__field_name',
        'grower__name',
        'grower__email',
        'transect_codes'
    )
    readonly_fields = ('submission_code', 'submitted_at', 'created_at', 'updated_at')
    autocomplete_fields = ['field', 'grower']
    fieldsets = (
        ('Application Information', {
            'fields': ('submission_code', 'field', 'grower', 'date_sampled')
        }),
        ('Transect Codes', {
            'fields': ('transect_code_1', 'transect_code_2', 'transect_code_3', 'transect_code_4'),
            'description': 'Transect codes specific to this application'
        }),
        ('Transect Coordinates', {
            'fields': (
                ('transect_1_latitude', 'transect_1_longitude'),
                ('transect_2_latitude', 'transect_2_longitude'),
                ('transect_3_latitude', 'transect_3_longitude'),
                ('transect_4_latitude', 'transect_4_longitude'),
            ),
            'description': 'GPS coordinates for each transect marker',
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_draft', 'is_submitted', 'submitted_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )




@admin.register(GrazingEvent)
class GrazingEventAdmin(admin.ModelAdmin):
    list_display = (
        'application',
        'event_number',
        'created_at'
    )
    list_filter = ('created_at',)
    search_fields = ('application__submission_code',)
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ['application']
    fieldsets = (
        ('Application & Event', {
            'fields': ('application', 'event_number')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(GrazingEventAnimal)
class GrazingEventAnimalAdmin(admin.ModelAdmin):
    list_display = (
        'grazing_event',
        'class_of_animal',
        'number_of_animals',
        'average_weight_lbs',
        'duration_days',
        'rest_period_days',
        'created_at'
    )
    list_filter = ('created_at',)
    search_fields = ('grazing_event__application__submission_code', 'class_of_animal')
    readonly_fields = ('created_at',)
    autocomplete_fields = ['grazing_event']
    fieldsets = (
        ('Grazing Event', {
            'fields': ('grazing_event',)
        }),
        ('Animal Information', {
            'fields': ('class_of_animal', 'number_of_animals', 'average_weight_lbs')
        }),
        ('Grazing Schedule', {
            'fields': ('duration_days', 'rest_period_days')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(CSVImportLog)
class CSVImportLogAdmin(admin.ModelAdmin):
    list_display = (
        'filename',
        'imported_by',
        'import_date',
        'status',
        'total_records',
        'successful_records',
        'failed_records'
    )
    list_filter = ('status', 'import_date')
    search_fields = ('filename', 'imported_by__name', 'imported_by__email')
    readonly_fields = ('import_date',)
    autocomplete_fields = ['imported_by']
    fieldsets = (
        ('File Information', {
            'fields': ('filename', 'imported_by', 'import_date')
        }),
        ('Import Status', {
            'fields': ('status', 'total_records', 'successful_records', 'failed_records')
        }),
        ('Error Log', {
            'fields': ('error_log',),
            'classes': ('collapse',)
        }),
    )


@admin.register(GrowerReport)
class GrowerReportAdmin(admin.ModelAdmin):
    list_display = (
        'application',
        'generated_at',
        'generated_by',
        'email_sent',
        'email_sent_at'
    )
@admin.register(TransectMeasurement)
class TransectMeasurementAdmin(admin.ModelAdmin):
    list_display = ('application', 'transect_index', 'transect_code', 'field_condition', 'updated_at')
    list_filter = ('field_condition', 'updated_at')
    search_fields = ('application__submission_code', 'transect_code')
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ['application']


@admin.register(DropPlateReading)
class DropPlateReadingAdmin(admin.ModelAdmin):
    list_display = ('measurement', 'distance_m', 'value')
    list_filter = ('distance_m',)
    autocomplete_fields = ['measurement']


@admin.register(VegetationReading)
class VegetationReadingAdmin(admin.ModelAdmin):
    list_display = ('measurement', 'metric', 'position_m', 'value')
    list_filter = ('metric', 'position_m')
    autocomplete_fields = ['measurement']


@admin.register(SoilReading)
class SoilReadingAdmin(admin.ModelAdmin):
    list_display = ('measurement', 'metric', 'position_m', 'value')
    list_filter = ('metric', 'position_m')
    autocomplete_fields = ['measurement']


@admin.register(SoilCompactionReading)
class SoilCompactionReadingAdmin(admin.ModelAdmin):
    list_display = ('measurement', 'position_m', 'max_value', 'score', 'hp')
    list_filter = ('position_m', 'score')
    autocomplete_fields = ['measurement']


@admin.register(InfiltrometerReading)
class InfiltrometerReadingAdmin(admin.ModelAdmin):
    list_display = ('measurement', 'time_mark', 'volume_ml')
    list_filter = ('time_mark',)
    autocomplete_fields = ['measurement']


@admin.register(InfiltrationRingReading)
class InfiltrationRingReadingAdmin(admin.ModelAdmin):
    list_display = ('measurement', 'pour_number', 'start_depth_cm', 'infiltration_time_sec', 'depth_after_15min_cm', 'change_in_depth_cm')
    list_filter = ('pour_number',)
    autocomplete_fields = ['measurement']





