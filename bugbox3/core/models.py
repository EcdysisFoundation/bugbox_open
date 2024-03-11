from django.contrib.gis.db.models import BigIntegerField, CharField, Model, MultiPolygonField


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
