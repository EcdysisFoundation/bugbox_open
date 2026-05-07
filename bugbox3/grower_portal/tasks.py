from celery import shared_task
from django.core.files.base import ContentFile
from django.db import transaction

from .models import LabelGeneration
from .services.label_generator import LabelGenerator


@shared_task(soft_time_limit=1500, time_limit=2000)
def generate_labels_async(label_generation_id: int):
    """
    Generate labels for a given label generation
    """
    with transaction.atomic():
        gen = LabelGeneration.objects.select_for_update().get(id=label_generation_id)
        gen.status = 'processing'
        gen.error_message = ''
        gen.save(update_fields=['status', 'error_message'])

    try:
        gen = LabelGeneration.objects.get(id=label_generation_id)
        params = gen.generation_params or {}

        project_type = gen.project_type
        label_category = gen.label_category
        cluster_number = gen.cluster_number
        year = gen.year

        generator = LabelGenerator(
            project_type=project_type,
            cluster_number=cluster_number,
            year=year,
            sample_types=params.get('sample_types', gen.sample_types or []),
            labels_per_type=params.get('labels_per_type', gen.labels_per_type or 0),
            created_by=gen.generated_by,
            label_category=label_category,
        )

        if project_type == 'ignite':
            if label_category == 'inner':
                num_sites = int(params.get('number_of_transects', 0))
                buffer, total_labels = generator.generate_quick_labels_ignite(num_sites)
                transect_codes_generated = generator.generated_codes
                filename = f"ignite_inner_{cluster_number}_{year}_labels.docx"
                sample_types = params.get('sample_types', gen.sample_types)
                labels_per_type = 4
            else:
                site_codes = params.get('site_codes', gen.transect_codes_generated or [])
                buffer, total_labels = generator.generate_outer_labels_ignite(site_codes)
                transect_codes_generated = site_codes
                filename = f"ignite_outer_{cluster_number}_{year}_labels.docx"
                sample_types = params.get('sample_types', gen.sample_types)
                labels_per_type = 1
        else:
            if label_category == 'inner':
                num_transects = int(params.get('number_of_transects', 0))
                buffer, total_labels = generator.generate_quick_labels_avalanche(num_transects)
                transect_codes_generated = generator.generated_codes
                filename = f"labels_quick_{project_type}_{cluster_number}_{year}.docx"
                sample_types = params.get('sample_types', gen.sample_types)
                labels_per_type = num_transects
            else:
                transect_codes = params.get('transect_codes', gen.transect_codes_generated or [])
                buffer, total_labels = generator.generate_outer_labels_avalanche(transect_codes)
                transect_codes_generated = transect_codes
                filename = f"labels_outer_{project_type}_{cluster_number}_{year}.docx"
                sample_types = []
                labels_per_type = 0

        buffer.seek(0)
        content = ContentFile(buffer.read())

        with transaction.atomic():
            gen = LabelGeneration.objects.select_for_update().get(id=label_generation_id)
            gen.sample_types = sample_types
            gen.labels_per_type = labels_per_type
            gen.total_labels_generated = total_labels
            gen.transect_codes_generated = transect_codes_generated
            gen.label_file.save(filename, content, save=False)
            gen.status = 'ready'
            gen.save()

    except Exception as e:
        with transaction.atomic():
            gen = LabelGeneration.objects.select_for_update().get(id=label_generation_id)
            gen.status = 'failed'
            gen.error_message = str(e)
            gen.save(update_fields=['status', 'error_message'])
        raise

