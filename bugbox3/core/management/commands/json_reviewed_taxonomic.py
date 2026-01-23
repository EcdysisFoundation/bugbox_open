import json

from django.apps import apps
from django.core.management.base import BaseCommand
from django.core.serializers.json import DjangoJSONEncoder

from bugbox3.samples import constants
from bugbox3.taxonomy import constants as taxon_constants


class Command(BaseCommand):
    """
    Create .json of specimen images with their taxonomic name.
    """

    SpecimenImage = apps.get_model(app_label='samples', model_name='SpecimenImage')
    Morphospecies = apps.get_model(app_label='taxonomy', model_name='Morphospecies')

    def handle(self, *args, **options):
        out_path = 'local_files/reviewed_taxonomic.json'
        p = 'specimen__classification__'
        fields = [
            'id',
            'specimen_id',
            constants.SPECIMEN_IMAGE_IMAGE,
            p + 'id',
            p + taxon_constants.FIELD_MORPHO_GBIF_PHYLUM,
            p + taxon_constants.FIELD_MORPHO_GBIF_CLASS,
            p + taxon_constants.FIELD_MORPHO_GBIF_ORDER,
            p + taxon_constants.FIELD_MORPHO_GBIF_FAMILY,
            p + taxon_constants.FIELD_MORPHO_GBIF_GENUS,
            p + taxon_constants.FIELD_MORPHO_GBIF_SPECIES,
            p + taxon_constants.FIELD_MORPHO_GBIF_CANONICAL_NAME,
            p + taxon_constants.FIELD_MORPHO_GBIF_RANK,
        ]

        q = list(self.SpecimenImage.objects.filter(
            specimen__classification_id__isnull=False,
            specimen__sample__site_visit__site__experiment__organization_id=constants.ECDYSIS_ORGANIZATION_ID).exclude(
                specimen__classification__name__icontains='eggs'
        ).exclude(
                specimen__classification__name__icontains='mummified'
        ).values(*fields))

        immature_ids = self.Morphospecies.objects.filter(name__icontains='immatures').values_list('id', flat=True)
        for i in q:
            if i[p + 'id'] in immature_ids:
                i.update({'immature_stage': True})
            else:
                i.update({'immature_stage': False})

        serialized_data = json.dumps(list(q), cls=DjangoJSONEncoder)

        # Parse the serialized data to ensure proper JSON formatting
        data = json.loads(serialized_data)

        with open(out_path, 'w') as f:
            json.dump(data, f)

        print(f'Completed, wrote {len(data)} recs')
