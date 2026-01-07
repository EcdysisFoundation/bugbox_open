from django.contrib.admin import ModelAdmin, site

from .models import PublicSiteContent, PrivateSiteContent


class PublicSiteContentAdmin(ModelAdmin):
    search_fields = ('title',)
    ordering = ['title']
    list_display = ['title', 'file', 'description', 'date_added']


class PrivateSiteContentAdmin(ModelAdmin):
    search_fields = ('title',)
    ordering = ['title']
    list_display = ['title', 'file', 'description', 'date_added']


site.register(PublicSiteContent, PublicSiteContentAdmin)
site.register(PrivateSiteContent, PrivateSiteContentAdmin)
