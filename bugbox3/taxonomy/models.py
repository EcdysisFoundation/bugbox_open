from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import (
    CASCADE,
    SET_NULL,
    CharField,
    DateField,
    DateTimeField,
    FloatField,
    ForeignKey,
    IntegerField,
    Model,
)

from . import constants


class Morphospecies(Model):
    name = CharField(max_length=64, unique=True)
    defunt_user = ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=SET_NULL)
    defunt_morpho = ForeignKey("self", null=True, on_delete=SET_NULL)
    defunt_date = DateTimeField(null=True)
    gbif_key = IntegerField(null=True, blank=True)
    gbif_class = CharField(max_length=64, blank=True)
    gbif_order = CharField(max_length=64, blank=True)
    gbif_family = CharField(max_length=64, blank=True)
    gbif_genus = CharField(max_length=64, blank=True)
    gbif_scientific_name = CharField(max_length=300, blank=True)
    gbif_canonical_name = CharField(max_length=300, blank=True)
    gbif_rank = CharField(max_length=50, blank=True)
    gbif_status = CharField(max_length=50, blank=True)
    subfamily = CharField(max_length=64, blank=True)
    bypass = FloatField(default=0, null=False, validators=[MaxValueValidator(100), MinValueValidator(0)])
    date_added = DateTimeField(auto_now_add=True)
    date_modified = DateTimeField(auto_now=True, auto_created=True)
    note = CharField(blank=True, max_length=500)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = 'Morphospecies'
        verbose_name_plural = 'Morphospecies'
        permissions = [
            (constants.PERMISSION_MORPHOSPECIES_FUNCTIONS, constants.PERMISSION_MORPHOSPECIES_FUNCTIONS_TXT),
        ]


class AiVersion(Model):
    version = CharField(max_length=64, unique=True)
    date = DateField(auto_now_add=True)


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
