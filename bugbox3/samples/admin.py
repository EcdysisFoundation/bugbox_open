from django.contrib.admin import ModelAdmin, site

from . models import Experiment, SamplePlan


class ExperimentAdmin(ModelAdmin):
    search_fields = ('name',)
    ordering = ['name']
    list_display = ['name']

class SamplePlanAdmin(ModelAdmin):
    search_fields = ('sample_type',)
    ordering = ['sample_type']
    list_display = ['sample_type']


site.register(Experiment, ExperimentAdmin)
site.register(SamplePlan, SamplePlanAdmin)
