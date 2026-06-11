from django.db import transaction
from django.db.models import (
    CASCADE,
    SET_NULL,
    CharField,
    DateTimeField,
    FileField,
    ForeignKey,
    Model,
    PositiveIntegerField,
)
from django.db.models.signals import post_save
from django.dispatch import receiver

from bugbox3.grower_portal.models.sample_codes import SampleCode

from . import constants
from .tasks import parse_taxa_file


class MicrobiomeTaxa(Model):
    """
    Files of microbiome analytic results from specific fastq analytic sets.
    """
    lab = CharField(
        max_length=100,
        choices=constants.LAB_CHOICES
    )
    lab_analytics_source = CharField(
        max_length=100,
        choices=constants.LAB_ANALYTIC_CHOICES
    )
    file = FileField(
        upload_to='microbiome',
        help_text='User download file')
    file_type = CharField(
        max_length=10,
        choices=constants.FILE_TYPE_CHOICES
    )
    target_region = CharField(
        max_length=10,
        choices=constants.TARGET_CHOICES)
    date_added = DateTimeField(auto_now_add=True)


@receiver(post_save, sender=MicrobiomeTaxa)
def uploaded_file_post_save(sender, instance, created, **kwargs):
    if created:
        transaction.on_commit(parse_taxa_file.s(instance.pk).delay)


class SiteMicrobiomeTaxa(Model):
    """
    Per site records of microbiome taxa from external files.
    """
    analytics_sample_id = CharField(max_length=100)
    site_code = CharField(max_length=50, blank=True)
    grower_site_code = ForeignKey(
        SampleCode,
        on_delete=SET_NULL,
        null=True,
    )
    user_file = FileField(
        upload_to='user_files',
        help_text='User download file')
    parent_file = ForeignKey(
        MicrobiomeTaxa,
        on_delete=CASCADE
    )
    sample_year = PositiveIntegerField()
    # aggreagated fields
    num_taxa_found = PositiveIntegerField(null=True)
    num_molecular_targets = PositiveIntegerField(null=True)
