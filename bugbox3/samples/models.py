import uuid

from django.db import models
from django.contrib.postgres.fields import ArrayField, HStoreField
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import pre_save

from . import constants
from ..taxonomy.models import Morphospecies, AiVersion

class Experiment(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    name = models.CharField(max_length=1000,unique=True)
    abb = models.CharField(max_length=10, null=True, blank=True)
    from_year = models.PositiveSmallIntegerField()
    to_year = models.PositiveSmallIntegerField()
    leader = models.CharField(max_length=1000)
    no_sites = models.PositiveIntegerField()
    date_per_site = models.PositiveIntegerField()
    sample_type = ArrayField(models.CharField(max_length=1000, blank=True))
    no_per_date = ArrayField(models.CharField(max_length=1000, blank=True))
    name_no_per_type = ArrayField(models.CharField(max_length=1000, blank=True))
    completed = models.BooleanField(default=False)
    summary = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'{self.name}'


class Sample(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    by_user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    site = models.CharField(max_length=1000, blank=True)
    country = models.CharField(max_length=1000, blank=True)
    state = models.CharField(max_length=1000, blank=True)
    county = models.CharField(max_length=1000, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    hc_type = models.CharField(max_length=1000, blank=True)
    treatment = models.CharField(max_length=1000, blank=True)
    date = models.DateField()
    type = models.CharField(max_length=1000, blank=True)
    name_no = models.CharField(max_length=1000, blank=True)
    notes = models.TextField(max_length=1000, null=True, blank=True)
    completed = models.BooleanField(default=False)
    image = models.ImageField(null=True, blank=True)
    classes = HStoreField(null=False, blank=True, default=constants.sample_taxon_classes_default)
    

class Specimen(models.Model):

    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    classification = models.ForeignKey(Morphospecies, on_delete=models.SET_NULL, null=True, blank=True)
    ai_classification = models.ForeignKey(Morphospecies, on_delete=models.SET_NULL,
                                          null=True, blank=True, related_name="ai")
    ai_version = models.ForeignKey(AiVersion, on_delete=models.SET_NULL, null=True, blank=True)
    sample = models.ForeignKey(Sample, on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    uploader = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="specimens_uploaded",
                                 null=True, on_delete=models.SET_NULL)
    partial_count = models.PositiveSmallIntegerField(blank=True, default=0, null=True)
    date_added = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True, auto_created=True)
    confidence = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    optional_pred_one = models.JSONField(default=None, null=True, blank=True)
    optional_pred_two = models.JSONField(default=None, null=True, blank=True)
    tags = ArrayField(models.CharField(max_length=1000, blank=True), default=list)
    acceptance = models.PositiveSmallIntegerField(choices=constants.ACCEPTANCE_CHOICES, blank=True, default=0)

    @property
    def image(self):
        """get the first image associated with this specimen if available"""
        try:
            return self.image_set.first().image
        except:
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


class SpecimenImage(models.Model):
    specimen = models.ForeignKey(Specimen, on_delete=models.CASCADE)
    primary = models.BooleanField(default=False)
    image = models.ImageField()
    date_added = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)

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


class TimelineEvent(models.Model):
    specimen = models.ForeignKey(Specimen, on_delete=models.CASCADE)
    event_title = models.CharField(max_length=200)
    date_time = models.DateTimeField(auto_now_add=True, auto_created=True)
    body = models.TextField()
    image_url = models.CharField(max_length=500)
