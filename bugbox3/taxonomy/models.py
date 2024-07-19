from django.conf import settings
from django.db.models import (
    CASCADE,
    SET_NULL,
    CharField,
    DateField,
    DateTimeField,
    FloatField,
    ForeignKey,
    ImageField,
    IntegerField,
    Model,
)
from django.db.models.signals import pre_save
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

    def __str__(self):
        return str(self.name)


@receiver(pre_save, sender=Morphospecies)
def save_thumbnail(sender, instance, **kwargs):
    """
    Signal receiver to save a thumbnail if there was a change.
    """
    # Ok to change to only save a thumbnail for this field.
    needs_thumbnail = False
    try:
        obj = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        # new record
        needs_thumbnail = True
    else:
        if not obj.image == instance.image:
            # Field has changed
            needs_thumbnail = True
    if needs_thumbnail and instance.image:
        instance.image_thumbnail = resized_thumbnail(
            instance.image,
            constants.MORPHPOSPECIES_THUMBSIZE,
            constants.MORPHPOSPECIES_THUMBSIZE)


class AiVersion(Model):
    version = CharField(max_length=64, unique=True)
    entered_date = DateField(auto_now_add=True)


class AiTraining(Model):
    morphospecies = ForeignKey(Morphospecies, on_delete=CASCADE, null=False)
    model = ForeignKey(AiVersion, on_delete=CASCADE, null=False)
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
