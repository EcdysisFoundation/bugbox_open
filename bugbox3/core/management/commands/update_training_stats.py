import csv

from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

class Command(BaseCommand):
    """
    Update AiTraining table with new stats.csv file.
    """
    Specimen = apps.get_model(app_label='samples', model_name='Specimen')
    AiTraining = apps.get_model('taxonomy', 'AiTraining')
    Morphospecies = apps.get_model('taxonomy', 'Morphospecies')
    PrivateSiteContent = apps.get_model('core', 'PrivateSiteContent')

    def handle(self, *args, **options):

        model_name = 'model_name'
        morphospecies_id = 'morphospecies_id'
        required_headers = ['', 'TP', 'FP', 'TN', 'FN', 'Precision', 'Recall', 'F1', 'Total_samples',
             model_name, 'morphos_name',
             'dataset_report_train', 'dataset_report_val',
             'dataset_report_test', 'dataset_report_morphos_name', 'dataset_report_total_samples']

        recent_dataset_report_stats = self.PrivateSiteContent.objects.filter(
            title__icontains='dataset_report_stats',
            file__icontains='dataset_report_stats').last()

        if not recent_dataset_report_stats:
            self.stdout.write(self.style.ERROR("No dataset report stats file found."))
            return

        with recent_dataset_report_stats.file.open('r') as csv_data:

            reader = csv.DictReader(csv_data)
            headers = list(reader.fieldnames)
            if not all(h in headers for h in required_headers):
                raise ValueError(f"Missing headers! {headers} != {required_headers}")
            # rename expected blank first header
            headers[0] = morphospecies_id
            reader.fieldnames = headers

            data = list(reader)
            if not data:
                self.stdout.write("File is empty.")
                return

            versions = list(set(row[model_name] for row in data))
            if len(versions) != 1:
                print(f'Error: Found {len(versions)} model versions, expected 1. Got: {versions}')
                return

            version = versions[0]

            self.stdout.write(f'Processing data for model version {version}')

            try:
                with transaction.atomic():
                    existing_count = self.AiTraining.objects.filter(model_name=version).count()
                    if existing_count > 0:
                        self.stdout.write(self.style.WARNING(
                            f"Found {existing_count} records for {version}. Skipping."
                        ))
                        return

                morpho_ids = set(row[morphospecies_id] for row in data if row[morphospecies_id])
                morpho_cache = {
                    m.id: m for m in self.Morphospecies.objects.filter(id__in=morpho_ids)
                }

                obs = []
                for d in data:
                    try:
                        m_id = int(d[morphospecies_id])
                        morpho_obj = morpho_cache.get(m_id)

                        if not morpho_obj:
                            print(f"Skipping row: Morphospecies ID {m_id} not found in database.")
                            continue

                        obs.append(self.AiTraining(
                            model_name=version,
                            morphospecies=morpho_obj,
                            total=int(d['dataset_report_total_samples']),
                            precision=float(d['Precision']),
                            recall=float(d['Recall']),
                            f1=float(d['F1']),
                            tp=int(d['TP']),
                            fp=int(d['FP']),
                            tn=int(d['TN']),
                            fn=int(d['FN']),
                            train=int(d['dataset_report_train']),
                            test=int(d['dataset_report_test']),
                            val=int(d['dataset_report_val']),
                        ))
                    except Exception as e:
                        print(f'Invalid data: {e} | Row: {d}')
                        return
                created = self.AiTraining.objects.bulk_create(obs)
                print(f'created {len(created)} records for model_name {version}')

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Transaction failed and rolled back: {e}"))
                return
