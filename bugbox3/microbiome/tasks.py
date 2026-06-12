import csv
import tempfile
from celery import chord
from celery.utils.log import get_task_logger

from django.apps import apps
from django.core.files.base import ContentFile

from bugbox3.grower_portal.models import SampleCode
from config import celery_app
from . import constants

# Celery-specific logger that plays nice with worker configurations
logger = get_task_logger(__name__)


def join_the_grower_site_code(microbiome_taxa_id):
    """
    Attempts to join the site_code from SampleCode for a single file.
    """
    logger.info(f"Starting site code join for microbiome_taxa_id: {microbiome_taxa_id}")
    SiteMicrobiomeTaxa = apps.get_model(app_label='microbiome', model_name='SiteMicrobiomeTaxa')

    site_microbiome_taxa_recs = SiteMicrobiomeTaxa.objects.filter(parent_file=microbiome_taxa_id)
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
        logger.info(f"Successfully updated {len(records_to_update)} records with grower site codes.")
    else:
        logger.info("No records required site code updates.")


def sample_year_from_id(sample_name):
    try:
        return int(sample_name[:4])
    except Exception:
        return 0


@celery_app.task(soft_time_limit=400)
def parse_taxa_file(taxa_file_id, chunk_size=20):
    """
    Master Task: Validates the file and orchestrates parallel chunk processing.
    """
    logger.info(f"Orchestrating parse for taxa file ID: {taxa_file_id}")
    MicrobiomeTaxa = apps.get_model(app_label='microbiome', model_name='MicrobiomeTaxa')

    try:
        file_rec = MicrobiomeTaxa.objects.get(id=taxa_file_id)
    except MicrobiomeTaxa.DoesNotExist:
        logger.error(f"MicrobiomeTaxa record {taxa_file_id} not found. Aborting.")
        return

    if file_rec.lab_analytics_source != constants.LAB_ECDYSIS_FOUNDATION:
        logger.warning(f"Unsupported lab source '{file_rec.lab_analytics_source}' for file ID {taxa_file_id}")
        return

    # Open file briefly to check headers and establish column count
    with file_rec.file.open('r') as csv_data:
        reader = csv.reader(csv_data, delimiter='\t')
        try:
            # We fetch headers to plan chunks.
            # Note: For massive files, reading headers only is better, but for 28MB list() is fine.
            rows = list(reader)
        except Exception as e:
            logger.error(f"Failed to read file ID {taxa_file_id}. Error: {e}", exc_info=True)
            raise e

    if len(rows) <= 2:
        logger.error(f"File ID {taxa_file_id} validation failed: Too few rows.")
        raise ValueError('There were too few rows.')
    if rows[0][0] != 'site_code' or rows[1][0] != '#OTU ID':
        logger.error(f"File ID {taxa_file_id} validation failed: Invalid layout headers.")
        raise ValueError('Unexpected file header structure.')

    num_data_columns = len(rows[0]) - 1
    logger.info(f"File ID {taxa_file_id} validated successfully. Columns to process: {num_data_columns}")

    # Build chunks of column indices (e.g., [[1, 2, 3], [4, 5, 6]])
    column_indices = list(range(1, num_data_columns + 1))
    chunks = [column_indices[i:i + chunk_size] for i in range(0, len(column_indices), chunk_size)]

    # Use a Celery Chord: Run chunks in parallel, then hit the cleanup callback
    header_tasks = [process_taxa_columns_chunk.si(taxa_file_id, chunk) for chunk in chunks]
    callback_task = after_parse_taxa_file.si(taxa_file_id)

    logger.info(f"Dispatching {len(chunks)} parallel chunk tasks for file ID {taxa_file_id}")
    chord(header_tasks)(callback_task)


@celery_app.task(soft_time_limit=300)
def process_taxa_columns_chunk(taxa_file_id, col_indices):
    """
    Worker Task: Processes a specific chunk of columns.
    Opening the file once per chunk balances I/O download costs with CPU/DB scaling.
    """
    logger.info(f"Starting chunk processing for file ID {taxa_file_id}. Columns: {col_indices}")
    MicrobiomeTaxa = apps.get_model(app_label='microbiome', model_name='MicrobiomeTaxa')
    SiteMicrobiomeTaxa = apps.get_model(app_label='microbiome', model_name='SiteMicrobiomeTaxa')

    file_rec = MicrobiomeTaxa.objects.get(id=taxa_file_id)

    with file_rec.file.open('r') as csv_data:
        rows = list(csv.reader(csv_data, delimiter='\t'))

    for col_idx in col_indices:
        try:
            site_code = rows[0][col_idx]
            sample_name = rows[1][col_idx]
            sample_year = sample_year_from_id(sample_name)

            data_rows = [[row[0], row[col_idx]] for row in rows]
            data = data_rows[2:]

            # Optimized inline aggregation calculation
            total = 0
            for v in data:
                try:
                    if float(v[1]) > 0.0:
                        total += 1
                except ValueError:
                    continue

            with tempfile.NamedTemporaryFile(mode='w+', suffix='.tsv', encoding='utf-8', newline='') as temp_file:
                writer = csv.writer(temp_file, delimiter='\t')
                writer.writerows(data_rows)
                temp_file.seek(0)

                django_file = ContentFile(temp_file.read().encode('utf-8'))
                filename = f"{sample_name}.tsv"

                # Single-row isolation ensures we don't hold global locks during file saves
                instance = SiteMicrobiomeTaxa(
                    site_code=site_code,
                    analytics_sample_id=sample_name,
                    parent_file=file_rec,
                    sample_year=sample_year,
                    num_taxa_found=total,
                    num_molecular_targets=len(data)
                )
                instance.user_file.save(filename, django_file, save=True)

            logger.info(f"Successfully processed column {col_idx} (Sample: {sample_name}) for file {taxa_file_id}")

        except Exception as e:
            logger.error(f"Critical error on column {col_idx} of file {taxa_file_id}: {e}", exc_info=True)
            raise e


@celery_app.task
def after_parse_taxa_file(taxa_file_id):
    """
    Callback Task: Executes only when all chunks have successfully finished.
    """
    logger.info(f"All chunks completed for file ID {taxa_file_id}. Running target post-processing.")
    join_the_grower_site_code(taxa_file_id)
    logger.info(f"Asynchronous processing pipeline finished perfectly for file ID {taxa_file_id}.")
