import csv
import tempfile

from django.apps import apps
from django.core.files import File

from bugbox3.samples.constants import ACCEPTANCE_PENDING


def build_training_csv_file(org_id, min_imgs, max_imgs) -> File:
    SpecimenImage = apps.get_model(app_label='samples', model_name='SpecimenImage')
    Morphospecies = apps.get_model(app_label='taxonomy', model_name='Morphospecies')
    # delete=False so Celery / Django can reopen the file by path.
    tmp = tempfile.NamedTemporaryFile(mode='w+', newline='', suffix='.csv', delete=False)
    writer = csv.writer(tmp)
    writer.writerow([
        'morphos_name', 'morphos_id', 'specimen_id', 'image',
        'gbif_canonical_name'
    ])

    morphospecies_set = Morphospecies.objects.exclude(name="incertae sedis")

    for morpho in morphospecies_set:
        specimen_images = SpecimenImage.objects.filter(
            specimen__classification_id=morpho.id,
            specimen__sample__site_visit__site__experiment__organization_id=org_id,
        ).exclude(
            specimen__acceptance=ACCEPTANCE_PENDING
        ).order_by('-id').values('specimen_id', 'image')[:max_imgs]

        if len(specimen_images) < min_imgs:
            continue

        for img in specimen_images:
            writer.writerow([
                morpho.name,
                morpho.id,
                img['specimen_id'],
                img['image'],
                morpho.gbif_canonical_name,
            ])

    # Flush and rewind so Django reads from the beginning.
    tmp.flush()
    tmp.seek(0)

    # Wrap in Django File so it can be assigned to a FileField.
    return File(tmp, name='training_selections.csv')
