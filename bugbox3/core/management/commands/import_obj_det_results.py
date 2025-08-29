import json
from datetime import datetime, timezone

from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    SpecimenImage = apps.get_model(
        app_label='samples', model_name='SpecimenImage')

    def handle(self, *args, **kwargs):

        if settings.ON_ECDYSIS_SERVER != 'YES':
            print('Currently this cmd is only supported on Ecdysis01')
            return

        json_path = 'local_files/obj_det_export1.json'

        with open(json_path, 'r') as file:
            data = json.load(file)
            saved = 0
            skipped = 0
            for i, d in enumerate(data):
                if 'label' in d.keys():
                    si = self.SpecimenImage.objects.get(
                        id=d['meta']['id'], specimen_id=d['meta']['specimen_id'])
                    if si.object_det_updated_at:
                        thedate = datetime.fromisoformat(d['updated_at'][:-1]).astimezone(timezone.utc)
                        if si.object_det_updated_at == thedate:
                            skipped += 1
                            continue
                    si.object_det_label = d['label']
                    si.object_det_annotation_id = d['annotation_id']
                    si.object_det_id = d['id']
                    si.object_det_updated_at = d['updated_at']
                    si.object_det_model_version = ''
                    si.save()
                    saved += 1
                else:
                    print(f'No label in item number {i}, skipping')
                    skipped += 1

            print('Completed, saved {0} new annotations, skipped {1}'.format(
                saved, skipped
            ))
