from datetime import datetime
from django.db.models import F, Value, Window, Count, Model, Q
from django.apps import apps
from django.core.management.base import BaseCommand
from django.db.models.functions import Concat, RowNumber


import csv

class Command(BaseCommand):
    """
        Select relevant fields in the tables and create a new table from them
    """
    Specimen = apps.get_model(app_label='samples', model_name='Specimen')

    SpecimenImage = apps.get_model(app_label='samples', model_name='SpecimenImage')
    Morphospecies = apps.get_model(app_label='taxonomy', model_name='Morphospecies')

    def handle(self, *args, **options):
        csv_path = 'bugbox3/core/management/commands/training_data/specimen_data.csv'

        with open(csv_path, mode='w', newline='') as file:
            writer = csv.writer(file)

            writer.writerow(['morphos_name', 'morphos_id','specimen_id', 'uuid','image',
                            'gbif_class_name','gbif_order','gbif_family','gbif_genus', 'specimen_count'])

            morphospecies_set = self.Morphospecies.objects.filter(~Q(name = "incertae sedis")).annotate(
                specimen_count=Count('specimen'),  # Count related specimens
                gbif_class_name = Concat(
                            F('specimen__classification__gbif_order'),
                            Value(' '),
                            F('specimen__classification__gbif_family'),
                            Value(' '),
                            F('specimen__classification__gbif_genus')
                )

            )

            for morpho in morphospecies_set:
                if morpho.specimen_count <= 1000 and morpho.specimen_count >= 20:
                    specimens = self.Specimen.objects.filter(
                        Q(classification_id=morpho.id) &
                        (Q(acceptance = 1) | Q(acceptance =2))
                    )

                    print(morpho.name + ": " + str(morpho.specimen_count) +" specimens")
                    for specimen in specimens:
                        images = self.SpecimenImage.objects.filter(specimen_id=specimen.id)
                        for image in images:
                        #     image.image = '/pool1/srv/bugbox3/bugbox3/media/' + str(image.image)
                        #     # image.image = 'C:/Users/ecdys\EmilyE\Work\images\'
                            writer.writerow([
                                morpho.name,
                                morpho.id,
                                specimen.id,
                                specimen.uuid,
                                image.image,
                                morpho.gbif_class_name,
                                morpho.gbif_order,
                                morpho.gbif_family,
                                morpho.gbif_genus,
                                morpho.specimen_count,
                                specimen.acceptance
                            ])

#         images = self.SpecimenImage.objects.all()[:1000]
#
#         for image in images:
#             specimen = Specimen.get(id = image.specimen_id)
#             morphos = Morphospecies.get(id = )
#
#
#
#         specimens = self.SpecimenImage.objects.select_related('specimen__classification').annotate(
#             morphos_name = F('specimen__classification__name'),
#             morphos_id = F('specimen__classification__id'),
#             gbif_class_name = Concat(
#                     F('specimen__classification__gbif_order'),
#                     Value(' '),
#                     F('specimen__classification__gbif_family'),
#                     Value(' '),
#                     F('specimen__classification__gbif_genus')
#                 ),
#                 gbif_order = F('specimen__classification__gbif_order'),
#                 gbif_family = F('specimen__classification__gbif_family'),
#                 gbif_genus = F('specimen__classification__gbif_genus'),
#                 spec_id = F('specimen__id'),
#                 uuid = F('specimen__uuid'),
#                 img = F('image'),
#                 image_id = F('id'),
#                 spec_count = Window(
#                     expression = RowNumber(),
#                     partition_by=[F('specimen__classification__name')],
#                     order_by=F('cnt').desc()
#                 )
#         )
#
#         for row in specimen:
#                 Specimen_Info.objects.create(
#                         morphos_name = row.morphos_name,
#                         morphos_id = row.morphos_id,
#                         gbif_class_name = row.gbif_class_name
#                         gbif_order = row.gbif_order
#                         gbif_family = row.gbif_family
#                         gbif_genus = row.gbif_genus
#                         uuid = row.uuid
#                         spec_image = row.img
#                         image_id = row.image_id
#                         spec_count = row.spec_count
#                 )
#
#         Specimen_Info.save()
