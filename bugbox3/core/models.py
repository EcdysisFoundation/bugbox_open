from django.contrib.gis.db.models import (CASCADE, BigIntegerField, CharField,
                                          DateTimeField, FileField, ForeignKey,
                                          JSONField, Manager, Model,
                                          MultiPolygonField, SlugField)
from django.db.models.fields import BLANK_CHOICE_DASH
from organizations.models import Organization

from .constants import FIELD_DISPLAY_TXT


class Exports(Model):
    organization = ForeignKey(Organization, related_name='exports', on_delete=CASCADE)
    title = SlugField(max_length=30)
    file = FileField(upload_to='exports')
    description = JSONField(default=dict)
    date_added = DateTimeField(auto_now_add=True)


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
