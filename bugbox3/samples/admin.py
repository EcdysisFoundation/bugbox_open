from django.contrib.admin import ModelAdmin, site

from .models import Experiment, SamplePlan, Site, Sample


class ExperimentAdmin(ModelAdmin):
    search_fields = ('name',)
    ordering = ['name']
    list_display = ['name']


class SamplePlanAdmin(ModelAdmin):
    search_fields = ('sample_type',)
    ordering = ['sample_type']
    list_display = ['sample_type']


class SiteAdmin(ModelAdmin):
    search_fields = ('site_name',)
    ordering = ['site_name']
    list_display = ['site_name']


class SampleAdmin(ModelAdmin):
    search_fields = ('uuid',)
    ordering = ['uuid']
    list_display = ['uuid']


site.register(Experiment, ExperimentAdmin)
site.register(SamplePlan, SamplePlanAdmin)
site.register(Site, SiteAdmin)
site.register(Sample, SampleAdmin)
