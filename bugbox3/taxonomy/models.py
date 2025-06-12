from io import BytesIO

from django.conf import settings
from django.db.models import (CASCADE, SET_NULL, BooleanField, CharField,
                              DateField, DateTimeField, FloatField, ForeignKey,
                              ImageField, IntegerField, Model, BigIntegerField)
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from ..libs.utilities import resized_thumbnail
from . import constants


class Morphospecies(Model):
    name = CharField(max_length=64, unique=True)
    defunt_user = ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=SET_NULL)
    defunt_morpho = ForeignKey("self", null=True, on_delete=SET_NULL)
    defunt_date = DateTimeField(null=True)
    gbif_key = IntegerField(null=True, blank=True)
    gbif_phylum = CharField(max_length=64, blank=True)
    gbif_class = CharField(max_length=64, blank=True)
    gbif_order = CharField(max_length=64, blank=True)
    gbif_family = CharField(max_length=64, blank=True)
    subfamily = CharField(max_length=64, blank=True)
    gbif_genus = CharField(max_length=64, blank=True)
    gbif_species = CharField(max_length=64, blank=True)
    gbif_scientific_name = CharField(max_length=300, blank=True)
    gbif_canonical_name = CharField(max_length=300, blank=True)
    gbif_rank = CharField(max_length=50, blank=True)
    gbif_status = CharField(max_length=50, blank=True)
    date_added = DateTimeField(auto_now_add=True)
    date_modified = DateTimeField(auto_now=True, auto_created=True)
    note = CharField(blank=True, max_length=2000)
    image = ImageField(upload_to='morpho_images/', null=True, blank=True)
    image_thumbnail = ImageField(upload_to='morpho_images/', null=True, blank=True)
    update_thumbs = BooleanField(null=True)
    exclude_from_export = BooleanField(default=False)
    class Meta:
        app_label = 'taxonomy'

    def __str__(self):
        return str(self.name)


@receiver(pre_save, sender=Morphospecies)
def set_update_thumbs(sender, instance, **kwargs):
    if instance.pk:
        obj = sender.objects.get(pk=instance.pk)
        if obj.image and (obj.image != instance.image):
            instance.update_thumbs = True


@receiver(post_save, sender=Morphospecies)
def save_thumbnail(instance, created, **kwargs):
    if created or instance.update_thumbs:
        buffer = None
        if instance.image:
            buffer = BytesIO()
            instance.image_thumbnail = resized_thumbnail(
                instance.image,
                constants.MORPHPOSPECIES_THUMBSIZE,
                constants.MORPHPOSPECIES_THUMBSIZE,
                buffer)
        else:
            instance.image_thumbnail = None
        instance.update_thumbs = None
        instance.save()
        if buffer:
            buffer.close()


class AiTraining(Model):
    morphospecies = ForeignKey(Morphospecies, on_delete=CASCADE, null=False)
    model_name = CharField(max_length=64)
    total = IntegerField(null=False)
    precision = FloatField(null=False)
    recall = FloatField(null=False)
    f1 = FloatField(null=False)
    tp = IntegerField(null=False)
    fp = IntegerField(null=False)
    tn = IntegerField(null=False)
    fn = IntegerField(null=False)
    train = IntegerField(null=False)
    test = IntegerField(null=False)
    val = IntegerField(null=False)
    entered_date = DateField(auto_now_add=True)

class GBIFImageRecord(Model):
    gbif_taxon_key = IntegerField()
    scientific_name = CharField(max_length=255)
    image_url = CharField(max_length=500)
    media_type = CharField(max_length=100, blank=True, null=True)
    license = CharField(max_length=255, blank=True, null=True)
    morphospecies = ForeignKey(Morphospecies, null=True, blank=True, on_delete=SET_NULL)
    date_fetched = DateTimeField(auto_now_add=True)
    decimal_latitude = FloatField(null=True, blank=True)
    decimal_longitude = FloatField(null=True, blank=True)
    occurrence_id = BigIntegerField(null=True, blank=True)
    downloaded_image = BooleanField(default=False)

    class Meta:
        app_label = 'taxonomy'
    def __str__(self):
        return f"{self.scientific_name} ({self.gbif_taxon_key})"


class FilteredGBIFImageRecord(Model):
    gbif_taxon_key = IntegerField()
    canonical_name = CharField(max_length=255)
    image_url = CharField(max_length=500)
    media_type = CharField(max_length=100, blank=True, null=True)
    license = CharField(max_length=255, blank=True, null=True)
    morphospecies = ForeignKey(Morphospecies, null=True, blank=True, on_delete=SET_NULL)
    date_fetched = DateTimeField(auto_now_add=True)
    decimal_latitude = FloatField(null=True, blank=True)
    decimal_longitude = FloatField(null=True, blank=True)
    occurrence_id = BigIntegerField(null=True, blank=True)
    downloaded_image = BooleanField(default=False)

    class Meta:
        app_label = 'taxonomy'
    def __str__(self):
        return f"{self.canonical_name} ({self.gbif_taxon_key})"