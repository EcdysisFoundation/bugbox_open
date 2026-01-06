from django.contrib.gis.db.models import (CASCADE, BigIntegerField, CharField,
                                          DateTimeField, FileField, ForeignKey,
                                          JSONField, Manager, Model,
                                          MultiPolygonField, PositiveIntegerField,
                                          SlugField)
from django.db.models.fields import BLANK_CHOICE_DASH
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from organizations.models import Organization

from .constants import FIELD_DISPLAY_TXT, FIELD_MORPHO_TAGS_LOOKUP
from .customstorage import PublicMediaStorage


class Exports(Model):
    organization = ForeignKey(Organization, related_name='exports', on_delete=CASCADE)
    title = SlugField(max_length=30)
    file = FileField(upload_to='exports')
    file_size = PositiveIntegerField(null=True, blank=True)
    description = JSONField(default=dict)
    date_added = DateTimeField(auto_now_add=True)


@receiver(post_save, sender=Exports)
def save_exports_file_size(instance, **kwargs):
    Exports.objects.filter(id=instance.id).update(file_size=instance.file.size)


class LookupChoicesManager(Manager):

    def user_access(self, user):
        return self.filter(organization__users=user)

    def get_field_choices(self, org_id, f):
        choices = [(v.entry, v.display_txt) for v in self.filter(
            organization_id=org_id,
            field=f
        ).order_by(FIELD_DISPLAY_TXT)]
        if not choices:
            choices = [BLANK_CHOICE_DASH[0],]
        return choices

    def get_field_choices_w_id(self, org_id, f):
        choices = [(v.entry, v.display_txt, v.id) for v in self.filter(
            organization_id=org_id,
            field=f
        ).order_by(FIELD_DISPLAY_TXT)]
        return choices

    def get_field_choices_w_blank(self, org_id, f):
        choices = [(v.entry, v.display_txt) for v in self.filter(
            organization_id=org_id,
            field=f
        ).order_by(FIELD_DISPLAY_TXT)]
        return [BLANK_CHOICE_DASH[0]] + choices

    def get_field_dict_w_blank(self, org_id, f):
        return {v[0]: v[1] for v in self.get_field_choices_w_blank(org_id, f)}


class LookupChoices(Model):
    organization = ForeignKey(Organization, related_name='lookup_choices', on_delete=CASCADE)
    field = CharField(max_length=20)
    entry = CharField(max_length=100)
    display_txt = CharField(max_length=100)

    objects = LookupChoicesManager()

    def __str__(self):
        return str(self.display_txt)


@receiver(post_delete, sender=LookupChoices)
def cleanup_orphaned_tags(sender, instance, **kwargs):
    """
    When a LookupChoices tag entry is deleted, this will remove that tag value
    from all Morphospecies and Specimen records that have it.
    """
    if instance.field == FIELD_MORPHO_TAGS_LOOKUP:
        from ..taxonomy.models import Morphospecies
        morphospecies_with_tag = Morphospecies.objects.filter(tags__contains=[instance.entry])
        for morpho in morphospecies_with_tag:
            if instance.entry in morpho.tags:
                morpho.tags.remove(instance.entry)
                morpho.save(update_fields=['tags'])
    elif instance.field == 'tags':
        from ..samples.models import Specimen
        specimens_with_tag = Specimen.objects.filter(tags__contains=[instance.entry])
        for specimen in specimens_with_tag:
            if instance.entry in specimen.tags:
                specimen.tags.remove(instance.entry)
                specimen.save(update_fields=['tags'])


class PublicSiteContent(Model):
    """
    Model for public media for the site, where default_acl is set to public-read.
    """
    title = SlugField(max_length=30, unique=True)
    file = FileField(storage=PublicMediaStorage(), upload_to='site_content')
    file_size = PositiveIntegerField(null=True, blank=True)
    description = CharField(max_length=500, blank=True)
    date_added = DateTimeField(auto_now_add=True)


@receiver(post_save, sender=PublicSiteContent)
def save_public_file_size(instance, **kwargs):
    PublicSiteContent.objects.filter(id=instance.id).update(file_size=instance.file.size)


class PrivateSiteContent(Model):
    """
    Model for media for the site requiring a presigned post to access.
    """
    title = SlugField(max_length=30, unique=True)
    file = FileField(upload_to='private_site_content')
    file_size = PositiveIntegerField(null=True, blank=True)
    description = CharField(max_length=500, blank=True)
    date_added = DateTimeField(auto_now_add=True)


@receiver(post_save, sender=PrivateSiteContent)
def save_private_file_size(instance, **kwargs):
    PrivateSiteContent.objects.filter(id=instance.id).update(file_size=instance.file.size)


class UsCounties(Model):
    """
    Simplified Census Bureaus MAF/TIGER geographic database.
    """
    statefp = CharField(max_length=2)
    countyfp = CharField(max_length=3)
    countyns = CharField(max_length=8)
    affgeoid = CharField(max_length=14)
    geoid = CharField(max_length=5)
    name = CharField(max_length=100)
    lsad = CharField(max_length=2)
    aland = BigIntegerField()
    awater = BigIntegerField()
    geom = MultiPolygonField(srid=4326)


class UsCountiesTigerLine(Model):
    """
    County and Equivalent Entity Nation-based Shapefile from the Census Bureaus MAF/TIGER geographic database.
    """
    statefp = CharField(max_length=2)
    countyfp = CharField(max_length=3)
    countyns = CharField(max_length=8)
    geoid = CharField(max_length=5)
    name = CharField(max_length=100)
    namelsad = CharField(max_length=100)
    lsad = CharField(max_length=2)
    classfp = CharField(max_length=2)
    mtfcc = CharField(max_length=5)
    csafp = CharField(null=True, max_length=3)
    cbsafp = CharField(null=True, max_length=5)
    metdivfp = CharField(null=True, max_length=5)
    funcstat = CharField(max_length=1)
    aland = BigIntegerField()
    awater = BigIntegerField()
    intptlat = CharField(max_length=11)
    intptlon = CharField(max_length=12)
    geom = MultiPolygonField(srid=4326)
