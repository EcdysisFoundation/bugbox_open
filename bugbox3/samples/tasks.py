import csv
import time
from tempfile import NamedTemporaryFile

from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile

from ..taxonomy.models import Morphospecies
from ..taxonomy.utils import get_skip_morphospecies_ids
from . import constants
from .calculations import get_indices
from .models import Experiment, Sample, Site, UserExperimentFile

User = get_user_model()


@shared_task(soft_time_limit=1500, hard_time_limit=2000)
def export_csv(
    user_id,
    experiment_id,
    indices,
    export_type,
    sample_types,
    include_skip_morph,
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
    if export_type == constants.EXP_CSV_TYPE_REVIEWED:
        unknown_species += ' or reviewed'
    skip_morphospecies_ids = get_skip_morphospecies_ids() if not include_skip_morph else []
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
            if not include_skip_morph and export_type != constants.EXP_CSV_TYPE_AI:
                specimens = specimens.exclude(classification_id__in=skip_morphospecies_ids)
            if not specimens.count() and not sample.completed:
                continue  # Skip incomplete/planned samples

            n = 0
            row = {
                constants.EXP_HEAD_ARR_EXPERIMENT: this_experiment.name,
                constants.EXP_HEAD_ARR_SITE: sample.site_visit.site.site_name,
                constants.EXP_HEAD_ARR_DATE: sample.site_visit.visit_date.strftime("%d-%b-%Y"),
                constants.EXP_HEAD_ARR_SAMPLE_TYPE: sample.sample_type,
                constants.EXP_HEAD_ARR_SAMPLE_NAME: sample.name_no,
                constants.EXP_HEAD_ARR_SAMPLE_COMPLETED: sample.completed,
                unknown_species: 0  # Starting count
            }
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

                if morphospecies_id:
                    morpho = Morphospecies.objects.get(id=morphospecies_id)
                    if morpho.gbif_class == "Arachnida":

                        if "Mites" in morpho.name or "Acari" in morpho.name:
                            continue

                    if level == "family":
                        name = morpho.gbif_family if morpho.gbif_family else "Unspecified Family"
                        morpho_headers[0][name] = morpho.gbif_order
                        morpho_headers[1][name] = morpho.gbif_family
                        morpho_headers[2][name] = ""
                    else:
                        if morpho.exclude_from_export:
                            print(f"Excluded from export (exclude_from_export=True): {morpho.name}")
                            continue
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
            if indices:
                indice_results = get_indices(n, row, headers_arr)
                for i in indices:
                    print(f"Writing {i}: {indice_results.get(i, '')}")
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
