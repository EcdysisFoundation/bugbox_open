import csv
import tempfile
from django.apps import apps
from django.db import transaction
from django.core.files.base import ContentFile

from config import celery_app
from bugbox3.grower_portal.models import SampleCode
from . import constants


def join_the_grower_site_code(microbiome_taxa_id):
    """
    Attempts to join the site_code from SampleCode
    """
    SiteMicrobiomeTaxa = apps.get_model(app_label='microbiome', model='SiteMicrobiomeTaxa')
    site_microbiome_taxa_recs = SiteMicrobiomeTaxa.objects.filter(
        parent_file=microbiome_taxa_id)
    site_codes = site_microbiome_taxa_recs.values_list('site_code', flat=True).distinct()
    sample_code_map = {
        sc.code: sc for sc in SampleCode.objects.filter(code__in=site_codes) if sc.code
    }
    records_to_update = []
    for rec in site_microbiome_taxa_recs:
        if not rec.site_code:
            continue

        sample_code_rec = sample_code_map.get(rec.site_code)
        if sample_code_rec:
            rec.grower_site_code = sample_code_rec
            records_to_update.append(rec)
    if records_to_update:
        SiteMicrobiomeTaxa.objects.bulk_update(records_to_update, ['grower_site_code'])


def join_grower_site_codes():
    """
    Run join_grower_site_code per site file.
    """
    MicrobiomeTaxa = apps.get_model(app_label='microbiome', model='MicrobiomeTaxa')
    analytics_files = MicrobiomeTaxa.objects.filter(
        lab_analytics_source=constants.LAB_ECDYSIS_FOUNDATION)
    for a in analytics_files:
        join_the_grower_site_code(a.id)


def sample_year_from_id(sample_name):
    # expected format like 2022_1_C6N03V
    try:
        return int(sample_name[:4])
    except Exception:
        return 0


@celery_app.task(soft_time_limit=240)
def parse_taxa_file(taxa_file_id):
    """
    Parse a file to a downloadable file and aggregated records per row.
    """
    MicrobiomeTaxa = apps.get_model(app_label='microbiome', model='MicrobiomeTaxa')
    file_rec = MicrobiomeTaxa.objects.get(id=taxa_file_id)
    if file_rec.lab_analytics_source == constants.LAB_ECDYSIS_FOUNDATION:
        with file_rec.file.open('r') as csv_data:
            # Expected file format is like
            # ['site_code', '1234', ...],
            # ['#OTU ID', '2022_1_C6N03V', ...],
            # ['d__Bacteria;__;__;__;__;__', 555.5, ...],
            # [...]]
            rows = list(csv.reader(csv_data, delimiter='\t'))

            # check for conformation of file
            if not len(rows) > 2:
                raise ValueError('There were too few rows.')
            if rows[0][0] != 'site_code':
                raise ValueError(
                    'Expected first row to be the site_code row, '
                    f'got {rows[0][0]} instead.')
            if rows[1][0] != '#OTU ID':
                raise ValueError(
                    'Expected first row to be the sample_code #OTU ID row, '
                    f'got {rows[1][0]} instead.')

            # Determine how many data columns exist (excluding the label column)
            num_data_columns = len(rows[0]) - 1

            def aggregate_values(data_rows):
                """
                Calculates aggregated values for each site file.
                Where, each row in data rows is len 2
                first two rows are headers
                column 1 is the molecular target
                column 2 is the abundance of that target
                """
                data = data_rows[2:]
                text_list = [v[1] for v in data]
                total = 0
                for value_str in text_list:
                    try:
                        value_float = float(value_str)
                        if value_float > 0.0:
                            total += 1
                    except ValueError:
                        continue
                return {
                    'num_taxa_found': total,
                    'num_molecular_targets': len(data)
                }
            try:
                with transaction.atomic():
                    # Loop through each data column index (1, 2, 3, etc.)
                    for col_idx in range(1, num_data_columns + 1):
                        site_code = rows[0][col_idx]
                        sample_name = rows[1][col_idx]
                        sample_year = sample_year_from_id(sample_name)
                        # Write out the 2-column table for this specific sample
                        with tempfile.NamedTemporaryFile(mode='w+', suffix='.tsv', encoding='utf-8', newline='') as temp_file:
                            writer = csv.writer(temp_file, delimiter='\t')

                            data_rows = [[row[0], row[col_idx]] for row in rows]
                            writer.writerow(data_rows)

                            # Reset the file pointer to the beginning before reading
                            temp_file.seek(0)

                            # Read the temporary content into a Django ContentFile
                            django_file = ContentFile(temp_file.read().encode('utf-8'))
                            filename = f"{sample_name}.tsv"
                            av = aggregate_values(data_rows)
                            instance = SiteMicrobiomeTaxa(
                                site_code=site_code,
                                analytics_sample_id=sample_name,
                                parent_file=file_rec,
                                sample_year=sample_year,
                                num_taxa_found=av['num_taxa_found'],
                                num_molecular_targets=av['num_molecular_targets'])
                            instance.user_file.save(filename, django_file, save=True)
            except Exception as e:
                print(f"Transaction failed and rolled back safely. Error: {e}")
                raise e
    else:
        print(
            f'file_rec.lab_analytics_source {file_rec.lab_analytics_source} \
              is not currently supported')
