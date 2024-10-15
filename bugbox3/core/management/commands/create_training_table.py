from datetime import datetime
from django.db.models import F, Value, CharField, 
Window, Count, Model, IntegerField, BigIntegerField, UUIDField
from django.apps import apps
from django.core.management.base import BaseCommand
from django.db.models.functions import Concat, RowNumber


class Specimen_Info(models.Model):
        morphos_name = models.CharField(max_length=64)
        morphos_id = models.BigIntegerField()
        gbif_class_name = models.CharField(max_length=255)
        gbif_order = models.CharField(max_length=64)
        gbif_family = models.CharField(max_length=64)
        gbif_genus = models.CharField(max_length=64)
        spec_id = models.BigIntegerField()
        uuid = models.UUIDField()
        spec_image = models.CharField(max_length=255)
        image_id = models.BigIntegerField()
        spec_count = models.IntegerField()
        
        def __str__(self):
                return self.morphos_name


class Command(BaseCommand):
    """
        Select relevant fields in the tables and create a new table from them
    """
    Specimen = apps.get_model(app_label='samples', model_name='Specimen')

    SpecimenImage = apps.get_model(app_label='samples', model_name='SpecimenImage')
    Morphospecies = apps.get_model(app_label='taxonomy', model_name='Morphospecies')

    def handle(self, *args, **options):
        specimens = self.SpecimenImage.objects.select_related('specimen__classification').annotate(
            morphos_name = F('specimen__classification__name'),
            morphos_id = F('specimen__classification__id'),
            gbif_class_name = Concat(
                    F('specimen__classification__gbif_order'),
                    Value(' '),
                    F('specimen__classification__gbif_family'),
                    Value(' '),
                    F('specimen__classification__gbif_genus')
                ),
                gbif_order = F('specimen__classification__gbif_order'),
                gbif_family = F('specimen__classification__gbif_family'),
                gbif_genus = F('specimen__classification__gbif_genus'),
                spec_id = F('specimen__id'),
                uuid = F('specimen__uuid'),
                img = F('image'),
                image_id = F('id'),
                spec_count = Window(
                    expression = RowNumber(),
                    partition_by=[F('specimen__classification__name')],
                    order_by=F('cnt').desc()
                )
        )
         
        for row in specimen:
                Specimen_Info.objects.create(
                        morphos_name = row.morphos_name,
                        morphos_id = row.morphos_id,
                        gbif_class_name = row.gbif_class_name
                        gbif_order = row.gbif_order
                        gbif_family = row.gbif_family
                        gbif_genus = row.gbif_genus
                        uuid = row.uuid
                        spec_image = row.img
                        image_id = row.image_id
                        spec_count = row.spec_count
                )

        Specimen_Info.save()
