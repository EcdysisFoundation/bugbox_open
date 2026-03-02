import uuid
from io import BytesIO

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.gis.db.models import PointField
from django.contrib.gis.geos import Point
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator
from django.db import transaction
from django.db.models import (
    CASCADE,
    SET_NULL,
    BooleanField,
    CharField,
    DateField,
    DateTimeField,
    DecimalField,
    FileField,
    ForeignKey,
    ImageField,
    Index,
    IntegerField,
    JSONField,
    Manager,
    Model,
    PositiveIntegerField,
    PositiveSmallIntegerField,
    SlugField,
    TextField,
    UUIDField,
)
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from organizations.models import Organization

from bugbox3.core import constants as geo_constants
from bugbox3.core.models import UsCountiesTigerLine

from ..libs.utilities import resized_thumbnail, save_specimen_img_thumbs
from ..taxonomy.models import Morphospecies
from ..taxonomy.tasks import id_image
from . import constants

User = get_user_model()


class UserLocationExportFile(Model):
    user = ForeignKey(User, on_delete=CASCADE)
    experiment = ForeignKey('samples.Experiment', on_delete=CASCADE)
    progress = IntegerField(default=0)
    file = FileField(upload_to='exports/location/')
    created_at = DateTimeField(auto_now_add=True)
    exported_file_status = CharField(
        max_length=10,
        choices=[('pending', 'Pending'), ('success', 'Success'), ('error', 'Error')],
        default='pending'
    )

    def __str__(self):
        return f"Location Export by {
            self.user} for {
            self.experiment} on {
            self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"


class ExperimentManager(Manager):
    def user_access(self, user):
        return self.filter(organization__users=user)


class Experiment(Model):
    organization = ForeignKey(Organization, related_name='experiment', on_delete=CASCADE)
    uuid = UUIDField(default=uuid.uuid4, unique=True)
    name = CharField(max_length=1000, unique=True)
    abbreviation = SlugField(max_length=20, unique=True)
    from_year = PositiveSmallIntegerField()
    to_year = PositiveSmallIntegerField()
    leader = CharField(max_length=1000)
    no_sites = PositiveIntegerField()
    date_per_site = PositiveIntegerField()
    completed = BooleanField(default=False)
    summary = TextField(null=True, blank=True)
    archived = CharField(max_length=3000, blank=True)

    objects = ExperimentManager()

    def __str__(self):
        return f'{self.name}'


class UserExperimentFile(Model):
    experiment = ForeignKey(Experiment, on_delete=CASCADE)
    user = ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE)
    file = FileField(max_length=100, upload_to='experiment/exported_data/')
    exported_file_status = CharField(max_length=40, null=True, blank=True)
    date_uploaded = DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.experiment.name} - {self.user.username}'


class UserExperimentAiFile(Model):
    user = ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE)
    experiment = ForeignKey(Experiment, on_delete=CASCADE)
    file = FileField(upload_to='experiment/ai_export/', null=True, blank=True)
    created_at = DateTimeField(auto_now_add=True)
    exported_file_status = CharField(
        max_length=10,
        choices=[('pending', 'Pending'), ('success', 'Success'), ('error', 'Error')],
        default='pending'
    )

    def __str__(self):
        return f"AI Export by {self.user} for {self.experiment} on {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"


class SamplePlanManager(Manager):
    def user_access(self, user):
        return self.filter(experiment__organization__users=user)


class SamplePlan(Model):
    experiment = ForeignKey(Experiment, on_delete=CASCADE)
    sample_type = CharField(max_length=100)
    no_per_date = PositiveSmallIntegerField(null=True, validators=[MaxValueValidator(100)])
    name_no_per_type = CharField(max_length=100, blank=True)

    objects = SamplePlanManager()


class SiteManager(Manager):
    def user_access(self, user):
        return self.filter(experiment__organization__users=user)


class Site(Model):
    experiment = ForeignKey(Experiment, on_delete=CASCADE)
    site_name = CharField(max_length=1000)
    habitat_type = CharField(max_length=100, blank=True)
    treatment = CharField(max_length=100, blank=True)
    gis_point = PointField(null=True)
    country = CharField(max_length=1000, blank=True)
    state_region = CharField(max_length=1000, blank=True)
    county_region = CharField(max_length=1000, blank=True)
    us_state_county_fips = CharField(blank=True, max_length=5)
    longitude = DecimalField(max_digits=9, decimal_places=6, null=True)
    latitude = DecimalField(max_digits=9, decimal_places=6, null=True)
    archived = CharField(max_length=3000, blank=True)

    objects = SiteManager()

    def save(self, *args, **kwargs):
        """
        Save a gis_point from the latitude, longitude since currently only these fields are in UI.
        """
        point = self.gis_point
        if self.longitude and self.latitude:
            try:
                longitude = float(self.longitude)
                latitude = float(self.latitude)
                point = Point(longitude, latitude, srid=4326)
            except Exception:
                raise ValidationError('Longitude and Latitude are not correctly formatted')
        if point:
            us_county = UsCountiesTigerLine.objects.filter(geom__contains=point)
            if len(us_county) == 1:
                self.country = geo_constants.UNITED_STATES
                us_county = us_county[0]
                fips = us_county.statefp + us_county.countyfp
                if us_county.statefp in geo_constants.FIPS_STATE:
                    self.state_region = geo_constants.FIPS_STATE[us_county.statefp]
                self.county_region = us_county.name
                self.us_state_county_fips = fips
        self.gis_point = point
        super(Site, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.site_name}'


class SiteVisitManager(Manager):
    def user_access(self, user):
        return self.filter(site__experiment__organization__users=user)


class SiteVisit(Model):
    uuid = UUIDField(default=uuid.uuid4, unique=True)
    site = ForeignKey(Site, on_delete=CASCADE)
    created_by_user = ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=SET_NULL)
    visit_date = DateField()
    sample_with_plan = BooleanField(default=True)
    notes = CharField(max_length=1000, blank=True)

    objects = SiteVisitManager()

    @property
    def has_related_data(self):
        """
        Indicate if a Sample label image has been uploaded or marked as completed or Specimens exist.
        """
        if self.sample_set.exclude(image='', completed=False):
            return True
        if Specimen.objects.filter(sample__site_visit_id=self.id):
            return True
        return False

    def save(self, *args, **kwargs):
        is_create = False
        if self.pk is None:
            is_create = True
        super(SiteVisit, self).save(*args, **kwargs)
        if is_create and self.sample_with_plan:
            # include samples according to plan
            plans = SamplePlan.objects.filter(experiment_id=self.site.experiment.id)
            for plan in plans:
                n = plan.no_per_date
                while n:
                    name = str(plan.name_no_per_type) + str(n)
                    Sample.objects.create(
                        site_visit_id=self.id,
                        sample_type=plan.sample_type,
                        name_no=name,
                        created_by_user=self.created_by_user)
                    n = n - 1

    class Meta:
        indexes = [
            Index(fields=['visit_date']),
        ]


class SampleManager(Manager):
    def user_access(self, user):
        return self.filter(site_visit__site__experiment__organization__users=user)


class Sample(Model):
    uuid = UUIDField(default=uuid.uuid4, unique=True)
    site_visit = ForeignKey(SiteVisit, on_delete=CASCADE)
    sample_type = CharField(max_length=100, blank=True)
    name_no = CharField(max_length=100, blank=True)
    notes = CharField(max_length=1000, blank=True)
    completed = BooleanField(default=False)
    image = ImageField(null=True, blank=True, upload_to='sample_images')
    image_thumbnail = ImageField(null=True, blank=True, upload_to='sample_images')
    created_by_user = ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=SET_NULL)
    update_thumbs = BooleanField(null=True)

    objects = SampleManager()

    class Meta:
        indexes = [
            Index(fields=['sample_type']),
        ]


@receiver(pre_save, sender=Sample)
def set_update_thumbs(sender, instance, **kwargs):
    if instance.pk:
        obj = sender.objects.get(pk=instance.pk)
        if obj.image and (obj.image != instance.image):
            instance.update_thumbs = True


@receiver(post_save, sender=Sample)
def save_thumbnail(instance, created, **kwargs):
    if created or instance.update_thumbs:
        buffer = None
        if instance.image:
            buffer = BytesIO()
            instance.image_thumbnail = resized_thumbnail(
                instance.image,
                constants.SAMPLE_IMAGE_THUMBSIZE,
                constants.SAMPLE_IMAGE_THUMBSIZE,
                buffer)
        else:
            instance.image_thumbnail = None
        instance.update_thumbs = None
        instance.save()
        if buffer:
            buffer.close()


class MultiSpecimenImageManager(Manager):
    def user_access(self, user):
        return self.filter(sample__site_visit__site__experiment__organization__users=user)


class MultiSpecimenImage(Model):
    sample = ForeignKey(Sample, on_delete=CASCADE)
    uuid = UUIDField(default=uuid.uuid4, unique=True)
    panorama_filename = CharField(max_length=100, blank=True)
    upload_dir_name = CharField(max_length=100, blank=True)
    annotations = JSONField(null=True, blank=True)
    annotations_updated_at = CharField(max_length=100, blank=True)
    annotations_segment = JSONField(null=True, blank=True)
    annotations_updated_at_segment = CharField(max_length=100, blank=True)
    predictions = JSONField(null=True, blank=True)
    predictions_timestamp = DateTimeField(null=True)
    predictions_coco = JSONField(null=True, blank=True)
    predictions_timestamp_coco = DateTimeField(null=True)
    image = ImageField(upload_to='multi_specimen_images')
    image_thumbnail = ImageField(null=True, blank=True, upload_to='multi_specimen_images')
    label_image = ImageField(null=True, blank=True, upload_to='multi_specimen_images')
    label_image_thumbnail = ImageField(null=True, blank=True, upload_to='multi_specimen_images')
    image_grid = CharField(
        max_length=10,
        choices=constants.MULTIIMAGE_IMAGE_GRID_CHOICES,
        blank=True)
    cropped_to_specimen = BooleanField(null=True)
    date_added = DateTimeField(auto_now_add=True)
    uploaded_by_user = ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=SET_NULL)

    objects = MultiSpecimenImageManager()


@receiver(post_save, sender=MultiSpecimenImage)
def save_multi_specimen_image_thumbnail(instance, created, **kwargs):
    # Can only create and delete MultiSpecimenImage.
    if created and instance.label_image:
        label_buffer = BytesIO()
        instance.label_image_thumbnail = resized_thumbnail(
            instance.label_image,
            constants.SAMPLE_IMAGE_THUMBSIZE,
            constants.SAMPLE_IMAGE_THUMBSIZE,
            label_buffer
        )
        instance.save()
        label_buffer.close()


class SpecimenManager(Manager):
    def user_access(self, user):
        return self.filter(sample__site_visit__site__experiment__organization__users=user)


class Specimen(Model):

    uuid = UUIDField(default=uuid.uuid4, unique=True)
    classification = ForeignKey(Morphospecies, on_delete=SET_NULL, null=True, blank=True)
    ai_classification = ForeignKey(Morphospecies, on_delete=SET_NULL,
                                   null=True, blank=True, related_name="ai")
    ai_model_name = CharField(max_length=64, blank=True)
    sample = ForeignKey(Sample, on_delete=SET_NULL, null=True, blank=True)
    reviewer_user = ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=SET_NULL)
    created_by_user = ForeignKey(settings.AUTH_USER_MODEL, related_name="specimens_uploaded",
                                 null=True, on_delete=SET_NULL)
    partial_count = PositiveSmallIntegerField(blank=True, default=0, null=True)
    date_added = DateTimeField(auto_now_add=True)
    date_modified = DateTimeField(auto_now=True, auto_created=True)
    confidence = DecimalField(max_digits=5, decimal_places=2, null=True)  # change to probability
    optional_pred_one = JSONField(default=None, null=True, blank=True)
    optional_pred_two = JSONField(default=None, null=True, blank=True)
    tags = ArrayField(CharField(max_length=1000, blank=True), default=list)
    acceptance = PositiveSmallIntegerField(choices=constants.ACCEPTANCE_CHOICES, blank=True, default=0)
    archival_identifier = CharField(max_length=1000, blank=True)
    archival_preservation = CharField(max_length=100, blank=True)
    archival_stored = CharField(max_length=100, blank=True)
    object_det_train = BooleanField(default=False)
    omit_from_training = BooleanField(default=False)

    objects = SpecimenManager()

    def __str__(self):
        return str(self.uuid)

    class Meta:
        permissions = [
            (constants.PERMISSION_SPECIMEN_REVIEW, constants.PERMISSION_SPECIMEN_REVIEW_TXT)
        ]
        indexes = [
            Index(fields=['sample']),
            Index(fields=['acceptance']),
            Index(fields=['classification']),
            Index(fields=['ai_classification']),
        ]


class SpecimenImageManager(Manager):
    def user_access(self, user):
        return self.filter(specimen__sample__site_visit__site__experiment__organization__users=user)


class SpecimenImage(Model):
    specimen = ForeignKey(Specimen, on_delete=CASCADE)
    multispecimen_image_uuid = UUIDField(null=True)
    multispecimen_image_index = PositiveSmallIntegerField(null=True)
    primary_image = BooleanField(default=False)
    public_image = BooleanField(default=False)
    downloaded_image = BooleanField(default=False)
    image = ImageField(upload_to='specimen_images')
    image_thumbnail = ImageField(null=True, blank=True, upload_to='specimen_images')
    image_thumbnail_medium = ImageField(null=True, blank=True, upload_to='specimen_images')
    image_thumbnail_large = ImageField(null=True, blank=True, upload_to='specimen_images')
    image_notfound = BooleanField(default=False)
    date_added = DateTimeField(auto_now_add=True)
    uploaded_by_user = ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=SET_NULL)
    image_width = PositiveIntegerField(null=True, blank=True)
    image_height = PositiveIntegerField(null=True, blank=True)
    image_thumbnail_large_width = PositiveIntegerField(null=True, blank=True)
    image_thumbnail_large_height = PositiveIntegerField(null=True, blank=True)
    # object_det fields based on image_thumbnail_large
    object_det_sent = DateTimeField(null=True)
    object_det_label = JSONField(null=True, blank=True)
    object_det_model_version = CharField(max_length=100, blank=True)
    object_det_annotation_id = PositiveIntegerField(null=True, help_text="From Label Studio")
    object_det_id = PositiveIntegerField(null=True, help_text="From Label Studio")
    object_det_updated_at = DateTimeField(null=True)

    objects = SpecimenImageManager()

    class Meta:
        ordering = ['-primary_image']


@receiver(pre_save, sender=SpecimenImage)
def ensure_single_true_flag(sender, instance, **kwargs):
    # Signal receiver to ensure only one instance has flag set to True.
    if instance.primary_image:
        # If flag is set to True, set flag to False for other instances
        SpecimenImage.objects.filter(specimen=instance.specimen).exclude(pk=instance.pk).update(primary_image=False)


@receiver(post_save, sender=SpecimenImage)
def save_specimen_image_thumbnail(instance, created, **kwargs):
    # Can only create and delete SpecimenImage image files through UI.
    if created and instance.image:
        save_specimen_img_thumbs(instance)


@receiver(post_save, sender=SpecimenImage)
def classify_new_images(sender, instance, created, **kwargs):
    # classify if it is a new image and meets criteria acceptence == Pending
    # and no previous classifications to the specimen.
    def signal_handler():
        if settings.AI_INFERENCE_URL:
            if created and instance.specimen.acceptance == \
                    constants.ACCEPTANCE_PENDING and not instance.specimen.ai_classification:
                id_image.delay(instance.specimen.id)
    transaction.on_commit(signal_handler)


class TimelineEventManager(Manager):
    def user_access(self, user):
        return self.filter(sample__site_visit__site__experiment__organization__users=user)


class TimelineEvent(Model):
    specimen = ForeignKey(Specimen, on_delete=CASCADE)
    event_title = CharField(max_length=200)
    date_time = DateTimeField(auto_now_add=True, auto_created=True)
    body = CharField(max_length=1000, blank=True)
    by_user = ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=SET_NULL)

    objects = TimelineEventManager()
