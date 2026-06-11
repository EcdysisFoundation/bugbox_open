from django.contrib.admin import ModelAdmin, site

from .models import MicrobiomeTaxa


class MicrobiomeTaxaAdmin(ModelAdmin):
    search_fields = ('file',)
    ordering = ['file']
    list_display = ['lab_analytics_source', 'target_region', 'file', 'date_added']


site.register(MicrobiomeTaxa, MicrobiomeTaxaAdmin)
