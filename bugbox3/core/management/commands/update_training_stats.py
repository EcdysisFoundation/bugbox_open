import csv

from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand

# from datetime import datetime


class Command(BaseCommand):
    """
    Update AiTraining table with new stats.csv file.
    """
    Specimen = apps.get_model(app_label='samples', model_name='Specimen')
    AiTraining = apps.get_model('taxonomy', 'AiTraining')
    Morphospecies = apps.get_model('taxonomy', 'Morphospecies')

    def handle(self, *args, **options):
        if settings.ON_ECDYSIS_SERVER != 'YES':
            print('Currently this cmd is only supported on Ecdysis01')
            return

        csv_path = 'local_files/dataset_report_stats.csv'
        model_name = 'model_name'
        morphospecies_id = 'morphospecies_id'
        h = ['', 'TP', 'FP', 'TN', 'FN', 'Precision', 'Recall', 'F1', 'Total_samples',
             model_name, 'morphos_name',
             'dataset_report_train', 'dataset_report_val',
             'dataset_report_test', 'dataset_report_morphos_name', 'dataset_report_total_samples']

        with open(csv_path, newline='') as file:
            reader = csv.reader(file)
            headers = next(reader)
            data = [row for row in reader]
            if headers == h:
                print('Headers read as expected')
            else:
                print('Headers not as expected, got..')
                print(headers)
                print('expected...')
                print(h)
                return
            h[0] = morphospecies_id

            version = [row[h.index(model_name)] for row in data]
            version = list(set(version))
            if len(version) != 1:
                print('More than one model_name version represented in file. Is this an error? got...')
                print(len)
                return
            else:
                version = version[0]

            print('Processing data for model version {0}'.format(version))
            print('Checking that model doesnt already have stats data....')

            v = self.AiTraining.objects.filter(model_name=version)
            if v:
                message = 'WARNING: {0} records with model_name = {1} already exist, exiting.'.format(
                    len(v), version
                )
                # or make function to delete existing to update
                print(message)
                return
            print('No previous entries, continuing ....')
            obs = []
            for d in data:
                try:
                    obs.append(self.AiTraining(
                        model_name=version,
                        morphospecies=self.Morphospecies.objects.get(
                            id=int(d[h.index(morphospecies_id)])),
                        total=int(d[h.index('dataset_report_total_samples')]),
                        precision=float(d[h.index('Precision')]),
                        recall=float(d[h.index('Recall')]),
                        f1=float(d[h.index('F1')]),
                        tp=int(d[h.index('TP')]),
                        fp=int(d[h.index('FP')]),
                        tn=int(d[h.index('TN')]),
                        fn=int(d[h.index('FN')]),
                        train=int(d[h.index('dataset_report_train')]),
                        test=int(d[h.index('dataset_report_test')]),
                        val=int(d[h.index('dataset_report_val')]),
                    ))
                except Exception as e:
                    print('invalid data encountered, exception ...')
                    print(e)
                    print('failing row...')
                    print(d)
                    return
            created = self.AiTraining.objects.bulk_create(
                obs)
            print(
                'created {0} AiTraining records for model_name {1}'.format(
                    len(created), version
                )
            )
