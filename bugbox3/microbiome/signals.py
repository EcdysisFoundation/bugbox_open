from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from bugbox3.grower_portal.models import GrowerSampleCodeMapping

from .tasks import join_microbiome_for_site_codes


@receiver(post_save, sender=GrowerSampleCodeMapping)
def link_microbiome_when_grower_mapped_to_sample_code(sender, instance, **kwargs):
    """
    auto connect existing microbiome rows to the grower sample code mapping when it is created
    """
    if not instance.sample_code_id:
        return

    site_code = instance.sample_code.code
    if not site_code:
        return

    transaction.on_commit(lambda: join_microbiome_for_site_codes([site_code]))
