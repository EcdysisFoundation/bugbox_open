import uuid

from django.conf import settings
from django.contrib.postgres.fields import ArrayField, HStoreField
from django.db.models import (Model, CharField, PositiveSmallIntegerField, 
                              BooleanField, PositiveIntegerField, TextField,
                              UUIDField, ForeignKey, DecimalField, ImageField,
                              DateField, DateTimeField, JSONField,
                              CASCADE, SET_NULL)
from django.db.models.signals import pre_save
from django.dispatch import receiver

from ..taxonomy.models import AiVersion, Morphospecies, Taxon
from . import constants


class Experiment(Model):
    uuid = UUIDField(default=uuid.uuid4, unique=True)
    name = CharField(max_length=1000, unique=True)
    abbreviation = CharField(max_length=10, blank=True)
    from_year = PositiveSmallIntegerField()
    to_year = PositiveSmallIntegerField()
    leader = CharField(max_length=1000)
    no_sites = PositiveIntegerField()
    date_per_site = PositiveIntegerField()
    completed = BooleanField(default=False)
    summary = TextField(null=True, blank=True)

    def __str__(self):
        return f'{self.name}'


class SampleType(Model):
    experiment = ForeignKey(Experiment, on_delete=CASCADE)
    sample_type = CharField(max_length=100, 
                            choices=constants.SAMPLE_TYPE_CHOICES_WO_BLANK)
    no_per_date = PositiveSmallIntegerField(null=True)
    name_no_per_type = CharField(max_length=100, blank=True)


class Sample(Model):
    uuid = UUIDField(default=uuid.uuid4, unique=True)
    experiment = ForeignKey(Experiment, on_delete=CASCADE)
    by_user = ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=SET_NULL)
    site = CharField(max_length=1000, blank=True)
    country = CharField(max_length=1000, blank=True)
    state = CharField(max_length=1000, blank=True)
    county = CharField(max_length=1000, blank=True)
    longitude = DecimalField(max_digits=9, decimal_places=6)
    latitude = DecimalField(max_digits=9, decimal_places=6)
    habitat_type = CharField(max_length=100, blank=True)
    treatment = CharField(max_length=100, blank=True)
    sample_date = DateField()
    sample_type = CharField(max_length=100, blank=True, 
                            choices=constants.SAMPLE_TYPE_CHOICES)
    name_no = CharField(max_length=100, blank=True)
    notes = TextField(max_length=1000, null=True, blank=True)
    completed = BooleanField(default=False)
    image = ImageField(null=True, blank=True)
    classes = HStoreField(null=False, blank=True, default=constants.sample_taxon_classes_default)


class Specimen(Model):

    uuid = UUIDField(default=uuid.uuid4, unique=True)
    classification = ForeignKey(Taxon, on_delete=SET_NULL, null=True, blank=True)
    morphospecies = ForeignKey(Morphospecies, on_delete=SET_NULL, null=True, blank=True)
    ai_classification = ForeignKey(Morphospecies, on_delete=SET_NULL,
                                          null=True, blank=True, related_name="ai")
    ai_version = ForeignKey(AiVersion, on_delete=SET_NULL, null=True, blank=True)
    sample = ForeignKey(Sample, on_delete=SET_NULL, null=True, blank=True)
    user = ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=SET_NULL)
    upload_user = ForeignKey(settings.AUTH_USER_MODEL, related_name="specimens_uploaded",
                                 null=True, on_delete=SET_NULL)
    partial_count = PositiveSmallIntegerField(blank=True, default=0, null=True)
    date_added = DateTimeField(auto_now_add=True)
    date_modified = DateTimeField(auto_now=True, auto_created=True)
    confidence = DecimalField(max_digits=5, decimal_places=2, null=True)
    optional_pred_one = JSONField(default=None, null=True, blank=True)
    optional_pred_two = JSONField(default=None, null=True, blank=True)
    tags = ArrayField(CharField(max_length=1000, blank=True), default=list)
    acceptance = PositiveSmallIntegerField(choices=constants.ACCEPTANCE_CHOICES, blank=True, default=0)
    archival_identifier = CharField(max_length=1000, blank=True, unique=True)
    archival_preservation = CharField(max_length=100, blank=True)
    archival_stored = CharField(max_length=100, blank=True)

    @property
    def image(self):
        """get the first image associated with this specimen if available"""
        try:
            return self.image_set.first().image
        except Exception:
            return None

    def save(self, *args, **kwargs):
        new_specimen = False
        if self.pk is None:
            """This code only happens on first create"""
            new_specimen = True
        super(Specimen, self).save(*args, **kwargs)

        if new_specimen:
            TimelineEvent.objects.create(specimen=self,
                                         event_title=self.user.name,
                                         body=self.user.name + " submitted this observation."
                                         )

    def __str__(self):
        return str(self.uuid)


class SpecimenImage(Model):
    specimen = ForeignKey(Specimen, on_delete=CASCADE)
    primary = BooleanField(default=False)
    image = ImageField()
    date_added = DateTimeField(auto_now_add=True)
    uploaded_by = ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=SET_NULL)

    class Meta:
        ordering = ['-primary']


@receiver(pre_save, sender=SpecimenImage)
def ensure_single_true_flag(sender, instance, **kwargs):
    """
    Signal receiver to ensure only one MyModel instance has flag set to True.
    """
    if instance.primary:
        # If flag is set to True, set flag to False for other instances
        SpecimenImage.objects.filter(specimen=instance.specimen).exclude(pk=instance.pk).update(primary=False)


class TimelineEvent(Model):
    specimen = ForeignKey(Specimen, on_delete=CASCADE)
    event_title = CharField(max_length=200)
    date_time = DateTimeField(auto_now_add=True, auto_created=True)
    body = TextField()
    image_url = CharField(max_length=500)
