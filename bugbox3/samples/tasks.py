import csv
import time
from tempfile import NamedTemporaryFile

from celery import shared_task
from celery.exceptions import SoftTimeLimitExceeded
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db.models import Q
from django.db.models.functions import Lower
from django.urls import reverse

from bugbox3.core.stitcher_utils import crop_img_to_annotations, crop_img_with_segmentation
from bugbox3.samples.models import (
    Experiment,
    MultiSpecimenImage,
    Sample,
    Site,
    SiteVisit,
    Specimen,
    SpecimenImage,
    UserExperimentAiFile,
    UserExperimentFile,
    UserLocationExportFile,
)
from config import celery_app

from ..taxonomy.models import Morphospecies
from ..taxonomy.utils import get_immature_morphospecies_ids, get_skip_morphospecies_ids
from . import constants
from .calculations import get_indices

User = get_user_model()


@shared_task(soft_time_limit=1500, hard_time_limit=2000)
def export_csv(
    user_id,
    experiment_id,
    indices,
    export_type,
    sample_types,
    include_immatures_skipped,
    sites,
    other_experiments,
    level
):
    user = User.objects.get(pk=user_id)
    experiment = Experiment.objects.user_access(user).get(id=experiment_id)
    indices = [v for v in indices if v in constants.INDICES_CHOICES_ALL]
    export_type = export_type if export_type in constants.EXPERIMENT_CSV_EXPORT_TYPES else None
    if not all([v.isnumeric() for v in sites]):
        None  # Handle invalid input
    sites = (
        [int(v) for v in sites]
        if sites
        else Site.objects.filter(experiment_id=experiment.id).values_list('id', flat=True))

    if not all([v.isnumeric() for v in other_experiments]):
        None  # Handle invalid input
    other_experiments = [int(v) for v in other_experiments]
    all_exp = other_experiments + [experiment.id]

    headers_arr = constants.EXP_HEADERS_ARR + indices
    morpho_headers = [dict.fromkeys(headers_arr, '') for _ in range(3)]
    unknown_species = 'Not identified'
    skip_morphospecies_ids = get_skip_morphospecies_ids()
    immature_morphospecies_ids = get_immature_morphospecies_ids()
    skip_ids_for_indices = skip_morphospecies_ids
    immature_ids_for_indices = immature_morphospecies_ids

    if include_immatures_skipped:
        skip_morphospecies_ids = []
        immature_morphospecies_ids = []

    if export_type == constants.EXP_CSV_TYPE_REVIEWED:
        unknown_species += ' or reviewed'

    all_species = {unknown_species}

    # Normalize level – if not "family", default to "morphospecies"
    if level != "family":
        level = "morphospecies"

    rows = []
    for exp_id in all_exp:
        try:
            this_experiment = Experiment.objects.user_access(user).get(id=exp_id)
        except Experiment.DoesNotExist:
            continue  # Skip non-existent experiments

        samples = Sample.objects.filter(
            site_visit__site__experiment_id=exp_id,
            sample_type__in=sample_types
        )
        if not other_experiments:
            samples = samples.filter(site_visit__site__in=sites)
        for sample in samples:
            specimens = sample.specimen_set
            if not include_immatures_skipped and export_type != constants.EXP_CSV_TYPE_AI:
                specimens = specimens.exclude(
                    classification_id__in=skip_morphospecies_ids + immature_morphospecies_ids)

            if not specimens.count() and not sample.completed:
                continue  # Skip incomplete/planned samples

            n = 0
            row = {
                constants.EXP_HEAD_ARR_EXPERIMENT: this_experiment.name,
                constants.EXP_HEAD_ARR_HABITAT: sample.site_visit.site.habitat_type,
                constants.EXP_HEAD_ARR_TREATMENT: sample.site_visit.site.treatment,
                constants.EXP_HEAD_ARR_SITE: sample.site_visit.site.site_name,
                constants.EXP_HEAD_ARR_DATE: sample.site_visit.visit_date.strftime("%d-%b-%Y"),
                constants.EXP_HEAD_ARR_SAMPLE_TYPE: sample.sample_type,
                constants.EXP_HEAD_ARR_SAMPLE_NAME: sample.name_no,
                constants.EXP_HEAD_ARR_SAMPLE_COMPLETED: sample.completed,
                unknown_species: 0  # Starting count
            }
            excluded_names_in_row = set()
            for specimen in specimens.all():
                if export_type == constants.EXP_CSV_TYPE_AI:
                    morphospecies_id = specimen.ai_classification_id
                elif export_type == constants.EXP_CSV_TYPE_REVIEWED:
                    morphospecies_id = (
                        None
                        if specimen.acceptance == constants.ACCEPTANCE_PENDING and specimen.ai_classification
                        else specimen.classification_id
                    )

                else:
                    morphospecies_id = (
                        specimen.classification_id
                        if specimen.classification_id
                        else specimen.ai_classification_id
                    )

                morpho = None
                if morphospecies_id:
                    morpho = Morphospecies.objects.get(id=morphospecies_id)

                    if level == "family":
                        name = morpho.gbif_family if morpho.gbif_family else "Unspecified Family"
                        morpho_headers[0][name] = morpho.gbif_order
                        morpho_headers[1][name] = morpho.gbif_family
                        morpho_headers[2][name] = ""
                    else:
                        name = morpho.name
                        morpho_headers[0][name] = morpho.gbif_order
                        morpho_headers[1][name] = morpho.gbif_family
                        morpho_headers[2][name] = morpho.gbif_species if morpho.gbif_species else morpho.gbif_genus
                else:
                    name = unknown_species
                    morpho_headers[0][name] = ''
                    morpho_headers[1][name] = ''
                    morpho_headers[2][name] = ''

                all_species.add(name)
                total = 1 + specimen.partial_count
                row[name] = row.get(name, 0) + total
                n += total

                if morphospecies_id in immature_ids_for_indices or morphospecies_id in skip_ids_for_indices:
                    excluded_names_in_row.add(name)
                if morpho and morpho.exclude_from_export:
                    excluded_names_in_row.add(name)

            if indices:
                excluded_names_for_indices = excluded_names_in_row.union({unknown_species})

                row_for_indices = {
                    k: v for k, v in row.items()
                    if k not in excluded_names_for_indices and k not in constants.EXP_HEADERS_ARR + indices
                }

                n_for_indices = sum(row_for_indices.values())

                indice_results = get_indices(n_for_indices, row_for_indices, headers_arr)
                for i in indices:
                    row[i] = indice_results.get(i, '')
            rows.append(row)

    timestr = time.strftime("%Y%m%d-%H%M%S")
    all_species.remove(unknown_species)  # Moving unknown to the front
    file_name = f"{experiment.abbreviation}-{timestr}.csv"

    # Using NamedTemporaryFile for memory efficiency
    with NamedTemporaryFile(delete=False, mode='w+', suffix='.csv') as temp_file:
        # Sort the species (or family) columns;
        final_fieldnames = headers_arr + [unknown_species] + sorted(list(all_species))
        writer = csv.DictWriter(temp_file, fieldnames=final_fieldnames)

        writer.writeheader()
        writer.writerows(morpho_headers)
        for row in rows:
            writer.writerow(row)
        temp_file.flush()

    with open(temp_file.name, 'rb') as f:
        user_experiment_file, created = UserExperimentFile.objects.get_or_create(user=user, experiment=experiment)
        user_experiment_file.file.save(file_name, ContentFile(f.read()), save=True)
        user_experiment_file.exported_file_status = 'success'
        user_experiment_file.save()

    return user_experiment_file.file.url


def _experiment_ai_csv_row(specimen, base_url):
    """Build one CSV data row from a specimen for AI expor"""
    link = base_url.rstrip('/') + reverse('samples:specimen', args=[specimen.id])
    site_name = ''
    visit_date = ''
    sample_type = ''
    sample_name = ''
    experiment_name = ''
    if specimen.sample and specimen.sample.site_visit and specimen.sample.site_visit.site:
        site = specimen.sample.site_visit.site
        site_name = site.site_name or ''
        if specimen.sample.site_visit.visit_date:
            visit_date = specimen.sample.site_visit.visit_date.strftime('%Y-%m-%d')
        sample_type = specimen.sample.sample_type or ''
        sample_name = f'{specimen.sample.name_no}' if specimen.sample.name_no else ''
        if getattr(site, 'experiment', None):
            experiment_name = site.experiment.name or ''
    c = specimen.classification
    ai = specimen.ai_classification
    opt1 = specimen.optional_pred_one or {}
    opt2 = specimen.optional_pred_two or {}
    class_name = c.name if c else ''
    top1 = 1 if (c and ai and c.id == ai.id) else 0
    top3 = 1 if (
        class_name and (
            (ai and class_name == ai.name) or
            class_name == opt1.get('class_op', '') or
            class_name == opt2.get('class_op', '')
        )
    ) else 0
    return [
        experiment_name,
        link,
        site_name,
        visit_date,
        sample_type,
        sample_name,
        class_name,
        c.gbif_class if c else '',
        c.gbif_order if c else '',
        c.gbif_family if c else '',
        c.gbif_canonical_name if c else '',
        specimen.ai_model_name or '',
        ai.name if ai else '',
        specimen.confidence or '',
        opt1.get('class_op', ''),
        opt1.get('pred_op', ''),
        opt2.get('class_op', ''),
        opt2.get('pred_op', ''),
        top1,
        top3,
    ]


@shared_task(soft_time_limit=1200, hard_time_limit=1500)
def export_ai_csv(
    user_id,
    experiment_id,
    sample_types,
    sites,
    other_experiments,
    base_url,
    ai_file_id,
):
    """Generate AI CSV export in background and save to UserExperimentAiFile."""
    user = User.objects.get(pk=user_id)
    ai_file = UserExperimentAiFile.objects.get(pk=ai_file_id)
    try:
        experiment = Experiment.objects.user_access(user).get(id=experiment_id)
    except Experiment.DoesNotExist:
        ai_file.exported_file_status = 'error'
        ai_file.save(update_fields=['exported_file_status'])
        return
    all_exp = other_experiments + [experiment.id]
    headers_arr = (
        [constants.EXPERIMENT_AI_CSV[0]] +
        ['Link', 'Site Name', 'Visit Date', 'Sample Type', 'Sample Name'] +
        constants.EXPERIMENT_AI_CSV[1:] +
        ['Top 1 Correct', 'Top 3 Correct']
    )
    specimens_objs = Specimen.objects.user_access(user).filter(
        sample__site_visit__site__experiment_id__in=all_exp,
        sample__sample_type__in=sample_types,
    ).exclude(
        acceptance=constants.ACCEPTANCE_PENDING,
    ).select_related(
        'sample__site_visit__site__experiment',
        'sample__site_visit__site',
        'sample__site_visit',
        'classification',
        'ai_classification',
    )
    if not other_experiments:
        specimens_objs = specimens_objs.filter(sample__site_visit__site__in=sites)
    else:
        specimens_objs = specimens_objs.order_by('sample__site_visit__site__experiment__name')

    try:
        timestr = time.strftime("%Y%m%d-%H%M%S")
        file_name = f"{experiment.abbreviation}-ai-{timestr}.csv"
        with NamedTemporaryFile(delete=False, mode='w', suffix='.csv', newline='', encoding='utf-8-sig') as temp_file:
            writer = csv.writer(temp_file)
            writer.writerow(headers_arr)
            for s in specimens_objs.iterator(chunk_size=500):
                writer.writerow(_experiment_ai_csv_row(s, base_url))
            temp_file.flush()
        with open(temp_file.name, 'rb') as f:
            ai_file.file.save(file_name, ContentFile(f.read()), save=True)
        ai_file.exported_file_status = 'success'
        ai_file.save(update_fields=['exported_file_status', 'file'])
    except Exception:
        ai_file.exported_file_status = 'error'
        ai_file.save(update_fields=['exported_file_status'])
        raise


@shared_task(soft_time_limit=3600, hard_time_limit=3900)
def export_csv_by_location(
        user_id,
        experiment_id,
        habitats,
        countries,
        states,
        indices,
        sample_types,
        include_immatures_skipped,
        level,
        export_type):
    user = User.objects.get(pk=user_id)
    experiment = Experiment.objects.user_access(user).get(id=experiment_id)
    habitats = [h.strip().lower() for h in habitats]
    countries = [c.strip().lower() for c in countries]
    states = [s.strip().lower() for s in states]
    sample_types = [s for s in sample_types if s]

    sites = Site.objects.all().annotate(
        norm_habitat=Lower('habitat_type'),
        norm_country=Lower('country'),
        norm_state=Lower('state_region')
    )

    filters = Q()
    if habitats:
        filters &= Q(norm_habitat__in=habitats)
    if countries:
        filters &= Q(norm_country__in=countries)
    if states:
        filters &= Q(norm_state__in=states)

    sites = sites.filter(filters)
    sitevisits = SiteVisit.objects.filter(site__in=sites)

    clean_sample_types = [t for t in sample_types if t]
    if clean_sample_types:
        samples = Sample.objects.filter(site_visit__in=sitevisits, sample_type__in=clean_sample_types)
    else:
        samples = Sample.objects.filter(site_visit__in=sitevisits)

    skip_ids = get_skip_morphospecies_ids()
    immature_ids = get_immature_morphospecies_ids()
    skip_ids_for_indices = skip_ids
    immature_ids_for_indices = immature_ids

    if include_immatures_skipped:
        skip_ids = []
        immature_ids = []

    unknown = 'Not identified'
    indices = [i for i in indices if i in constants.INDICES_CHOICES_ALL]
    headers_arr = constants.EXP_HEADERS_ARR + indices
    morpho_headers = [dict.fromkeys(headers_arr, '') for _ in range(3)]

    user_file = UserLocationExportFile.objects.create(
        user=user,
        experiment=experiment,
        exported_file_status='pending',
        progress=0
    )

    all_species = {unknown}
    rows = []

    total = samples.count()
    for i, sample in enumerate(samples.select_related('site_visit__site'), start=1):
        site = sample.site_visit.site
        specimens = sample.specimen_set.all()

        if not include_immatures_skipped:
            specimens = specimens.exclude(classification_id__in=skip_ids + immature_ids)

        if not specimens.exists() and not sample.completed:
            continue

        row = {
            constants.EXP_HEAD_ARR_EXPERIMENT: experiment.name,
            constants.EXP_HEAD_ARR_HABITAT: site.habitat_type,
            constants.EXP_HEAD_ARR_TREATMENT: site.treatment,
            constants.EXP_HEAD_ARR_SITE: site.site_name,
            constants.EXP_HEAD_ARR_DATE: sample.site_visit.visit_date.strftime("%d-%b-%Y"),
            constants.EXP_HEAD_ARR_SAMPLE_TYPE: sample.sample_type,
            constants.EXP_HEAD_ARR_SAMPLE_NAME: sample.name_no,
            constants.EXP_HEAD_ARR_SAMPLE_COMPLETED: sample.completed,
            unknown: 0
        }

        excluded_names = set()
        for specimen in specimens:
            if export_type == constants.EXP_CSV_TYPE_AI:
                morphospecies_id = specimen.ai_classification_id
            elif export_type == constants.EXP_CSV_TYPE_REVIEWED:
                morphospecies_id = (
                    None
                    if specimen.acceptance == constants.ACCEPTANCE_PENDING
                    and specimen.ai_classification
                    else specimen.classification_id
                )
            else:
                morphospecies_id = specimen.classification_id or specimen.ai_classification_id

            morpho = None
            if morphospecies_id:
                morpho = Morphospecies.objects.get(id=morphospecies_id)

                if level == "family":
                    name = morpho.gbif_family if morpho.gbif_family else "Unspecified Family"
                    morpho_headers[0][name] = morpho.gbif_order
                    morpho_headers[1][name] = morpho.gbif_family
                    morpho_headers[2][name] = ""
                else:
                    name = morpho.name
                    morpho_headers[0][name] = morpho.gbif_order
                    morpho_headers[1][name] = morpho.gbif_family
                    morpho_headers[2][name] = morpho.gbif_species or morpho.gbif_genus

            else:
                name = unknown
                morpho_headers[0][name] = morpho_headers[1][name] = morpho_headers[2][name] = ''

            all_species.add(name)
            total_count = 1 + specimen.partial_count
            row[name] = row.get(name, 0) + total_count

            if morphospecies_id in skip_ids_for_indices or morphospecies_id in immature_ids_for_indices:
                excluded_names.add(name)
            if morpho and morpho.exclude_from_export:
                excluded_names.add(name)

        if indices:
            excluded_names_for_indices = excluded_names.union({unknown})
            clean_row = {
                k: v for k, v in row.items()
                if k not in excluded_names_for_indices and k not in constants.EXP_HEADERS_ARR + indices
            }

            n = sum(clean_row.values())
            index_results = get_indices(n, clean_row, headers_arr)
            for i_key in indices:
                row[i_key] = index_results.get(i_key, '')

        rows.append(row)

        if i % max(1, total // 20) == 0 or i == total:
            user_file.progress = int((i / total) * 100)
            user_file.save(update_fields=["progress"])

    all_species.discard(unknown)
    filename = f"{experiment.abbreviation}-LocationExport-{time.strftime('%Y%m%d-%H%M%S')}.csv"
    final_headers = headers_arr + [unknown] + sorted(all_species)

    with NamedTemporaryFile(delete=False, mode='w+', suffix='.csv') as temp_file:
        writer = csv.DictWriter(temp_file, fieldnames=final_headers)
        writer.writeheader()
        writer.writerows(morpho_headers)
        for row in rows:
            writer.writerow(row)
        temp_file.flush()

    with open(temp_file.name, 'rb') as f:
        user_file.file.save(filename, ContentFile(f.read()), save=True)
        user_file.exported_file_status = 'success'
        user_file.progress = 100
        user_file.save()

    return user_file.file.url


@celery_app.task(soft_time_limit=240)
def crop_panorama(img_ids, sample_id, user_id):
    if settings.ON_ECDYSIS_SERVER != 'YES':
        # High memory usage, run only on local server
        return
    try:
        sample = Sample.objects.get(id=sample_id)
        user = User.objects.get(id=user_id)
        images = MultiSpecimenImage.objects.filter(id__in=img_ids)
    except Exception as e:
        print(f'Warning: {e}')
        return
    if not images:
        return

    for i in images:
        if not i.annotations:
            continue
        try:
            imgs = crop_img_to_annotations(i.image, i.annotations)
        except SoftTimeLimitExceeded:
            return
        if imgs:
            for cropped_i in imgs:
                specimen = Specimen.objects.create(
                    sample=sample,
                    created_by_user=user)
                SpecimenImage.objects.create(
                    specimen=specimen,
                    image=cropped_i[0],
                    multispecimen_image_uuid=i.uuid,
                    multispecimen_image_index=cropped_i[1],
                    uploaded_by_user=user
                )
                cropped_i[0].close()
            i.cropped_to_specimen = True
            i.save()


@celery_app.task(soft_time_limit=240)
def crop_panorama_segmentation(img_ids, sample_id, user_id):
    if settings.ON_ECDYSIS_SERVER != 'YES':
        # High memory usage, run only on local server
        return
    try:
        sample_instance = Sample.objects.get(id=sample_id)
        user_instance = User.objects.get(id=user_id)
    except Exception as e:
        print(f'Warning: {e}')
        return
    for v in img_ids:
        i = MultiSpecimenImage.objects.get(id=v)
        if not i.annotations_segment:
            continue
        try:
            success = crop_img_with_segmentation(
                i.image,
                i.annotations_segment,
                sample_instance,
                user_instance,
                i.uuid)

        except SoftTimeLimitExceeded:
            return

        i.cropped_to_specimen = success
        i.save()
