from django.contrib.admin import ModelAdmin, site

from . models import Experiment


class ExperimentAdmin(ModelAdmin):
    search_fields = ('name',)
    ordering = ['name']
    list_display = ['name']


site.register(Experiment, ExperimentAdmin)