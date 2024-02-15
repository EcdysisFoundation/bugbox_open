from django.dispatch import receiver
from django.contrib.postgres.indexes import GinIndex, OpClass
from django.db.models import (Model, IntegerField, CharField, ForeignKey, 
                              FloatField, DateTimeField, DateField,
                              CASCADE, SET_NULL)
from django.db.models.signals import post_save
from django.db.models.functions import Lower
from django.core.validators import MaxValueValidator, MinValueValidator
from django.conf import settings


class Taxon(Model):
    """from the GBIF backbone-current 'Taxon.tsv' """
    taxon_id = IntegerField(primary_key=True)
    dataset_id = CharField(blank=True, max_length=50)
    parent_name_usage = ForeignKey('Taxon', on_delete=CASCADE, null=True)
    accepted_name_usage_id = IntegerField(null=True, blank=True)
    original_name_usage_id = IntegerField(null=True, blank=True)
    scientific_name = CharField(blank=True, max_length=300)
    scientific_name_authorship = CharField(blank=True, max_length=300)
    canonical_name = CharField(blank=True, max_length=100)
    generic_name = CharField(blank=True, max_length=100)
    specific_epithet = CharField(blank=True, max_length=100)
    infraspecific_epithet = CharField(blank=True, max_length=100)
    taxon_rank = CharField(blank=True, max_length=50)
    name_published_in = CharField(blank=True, max_length=1000)
    taxonomic_status = CharField(blank=True, max_length=50)
    taxon_remarks = CharField(blank=True, max_length=200)
    kingdom = CharField(blank=True, max_length=50)
    phylum = CharField(blank=True, max_length=50)
    taxon_class = CharField(blank=True, max_length=50)
    taxon_order = CharField(blank=True, max_length=50)
    taxon_family = CharField(blank=True, max_length=50)
    genus = CharField(blank=True, max_length=50)

    class Meta:
        indexes = [GinIndex(OpClass(Lower('canonical_name'), name='gin_trgm_ops'), name='lower_canonical_name_idx')]
        verbose_name = 'Taxon'
        verbose_name_plural = 'Taxa'

    def __str__(self):
        return str(self.canonical_name)

    def ancestor_list(self):
        ancestor_list = list()

        def get_parent(node, ancestor_list):
            if node.parent_name_usage is not None:
                parent = node.parent_name_usage
                ancestor_list.append(parent)
                get_parent(parent, ancestor_list)

        get_parent(self, ancestor_list)
        return ancestor_list


class Morphospecies(Model):
    name = CharField(max_length=64, unique=True)
    taxon = ForeignKey(Taxon, on_delete=CASCADE, null=True, blank=True)
    defunt_user = ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=SET_NULL)
    defunt_morpho = ForeignKey("self", null=True, on_delete=SET_NULL)
    defunt_date = DateTimeField(null=True)
    taxon_class = CharField(max_length=64, null=True, blank=True)
    order = CharField(max_length=64, null=True, blank=True)
    family = CharField(max_length=64, null=True, blank=True)
    subfamily = CharField(max_length=64, null=True, blank=True)
    genus = CharField(max_length=64, null=True, blank=True)
    species = CharField(max_length=64, null=True, blank=True)
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
            ("use_morphospecies_functions", "Can use the “Merge” button, check the “Bypass” box or change the percent threshold"),
        ]


@receiver(post_save, sender=Morphospecies)
def ensure_single_true_flag(sender, instance, **kwargs):
    """
    Signal receiver to update classification to the new classification.
    """

    instance.specimen_set.update(classification_id=instance.taxon_id)


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
