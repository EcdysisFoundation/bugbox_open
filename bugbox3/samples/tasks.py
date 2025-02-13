from celery import shared_task
from django.apps import apps
from django.conf import settings
from . import constants
from .models import Site, Experiment, Sample
from ..taxonomy.utils import get_skip_morphospecies_ids
from ..taxonomy.models import Morphospecies
from .calculations import get_indices
import time
import csv
import os
from django.core.files.storage import default_storage
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from io import StringIO


User = get_user_model()


@shared_task
def export_csv(user_id, experiment_id, indices, export_type, sample_types, include_skip_morph, sites, other_experiments, level):
    user = User.objects.get(pk=user_id)
    experiment = Experiment.objects.user_access(user).get(id=experiment_id)


    indices = [v for v in indices if v in constants.INDICES_CHOICES_ALL]
    export_type = export_type if export_type in constants.EXPERIMENT_CSV_EXPORT_TYPES else None
    if not all([v.isnumeric() for v in sites]):
        # return HttpResponse(status=404)
        None
    sites = [int(v) for v in sites]
    if not sites:
        sites = Site.objects.filter(experiment_id=experiment.id).values_list('id', flat=True)
    if not all([v.isnumeric() for v in other_experiments]):
        # return HttpResponse(status=404)
        None
    other_experiments = [int(v) for v in other_experiments]
    all_exp = other_experiments + [experiment.id]
    headers_arr = constants.EXP_HEADERS_ARR + indices
    morpho_headers = [dict.fromkeys(headers_arr, '') for _ in range(3)]
    unknown_species = 'Not identified'
    if export_type == constants.EXP_CSV_TYPE_REVIEWED:
        unknown_species += ' or reviewed'
    if not include_skip_morph:
        skip_morphospecies_ids = get_skip_morphospecies_ids()
    else:
        skip_morphospecies_ids = []
    all_species = {unknown_species}

    rows = []
    for exp_id in all_exp:
        try:
            this_experiment = Experiment.objects.user_access(user).get(id=exp_id)
        except Experiment.DoesNotExist:
            # raise Http404
            None
        samples = Sample.objects.filter(
            site_visit__site__experiment_id=exp_id,
            sample_type__in=sample_types
        )
        if not other_experiments:
            samples = samples.filter(
                site_visit__site__in=sites
            )
        for sample in samples:
            specimens = sample.specimen_set
            if not include_skip_morph and export_type != constants.EXP_CSV_TYPE_AI:
                specimens = specimens.exclude(classification_id__in=skip_morphospecies_ids)
            if not specimens.count() and not sample.completed:
                # indicates a planned sample that was not actually taken or completed
                continue
            n = 0
            row = {
                constants.EXP_HEAD_ARR_EXPERIMENT: this_experiment.name,
                constants.EXP_HEAD_ARR_SITE: sample.site_visit.site.site_name,
                constants.EXP_HEAD_ARR_DATE: sample.site_visit.visit_date.strftime("%d-%b-%Y"),
                constants.EXP_HEAD_ARR_SAMPLE_TYPE: sample.sample_type,
                constants.EXP_HEAD_ARR_SAMPLE_NAME: sample.name_no,
                constants.EXP_HEAD_ARR_SAMPLE_COMPLETED: sample.completed,
                unknown_species: 0  # starting count
            }
            family_data = {}
            for specimen in specimens.all():
                if export_type == constants.EXP_CSV_TYPE_AI:
                    morphospecies_id = specimen.ai_classification_id
                elif export_type == constants.EXP_CSV_TYPE_REVIEWED:
                    if specimen.acceptance == constants.ACCEPTANCE_PENDING and specimen.ai_classification:
                        morphospecies_id = None
                    else:
                        morphospecies_id = specimen.classification_id
                else:
                    # must be the all selection, prioritize classifcation_id
                    if specimen.classification_id:
                        morphospecies_id = specimen.classification_id
                    else:
                        morphospecies_id = specimen.ai_classification_id
                if morphospecies_id:
                    morpho = Morphospecies.objects.get(id=morphospecies_id)
                    name = morpho.name
                    family = morpho.gbif_family
                else:
                    name = unknown_species
                    family = unknown_species
                all_species.add(name)
                total = 1 + specimen.partial_count
                if level == constants.EXP_CSV_TYPE_FAMILY:
                    if family in family_data:
                        family_data[family] += total
                    else:
                        family_data[family] = total
                else:
                    if name in row.keys():
                        row[name] += total
                    else:
                        row[name] = total
                n += 1 + specimen.partial_count
            if level == constants.EXP_CSV_TYPE_FAMILY:
                for family, count in family_data.items():
                    row[family] = count
            if indices:
                indice_results = get_indices(n, row, headers_arr)
                for i in indices:
                    row[i] = indice_results[i]

            rows.append(row)
    timestr = time.strftime("%Y%m%d-%H%M%S")
    all_species.remove(unknown_species)  # moving unknown to the front
    # response = HttpResponse(content_type='text/csv')
    # response['Content-Disposition'] = 'attachment; filename="{0}-{1}.csv"'.format(
    #     experiment.abbreviation, timestr)
    # writer = csv.DictWriter(response, headers_arr + [unknown_species] + sorted(list(all_species)), 0)
    # writer.writeheader()
    # writer.writerows(morpho_headers)
    # writer.writerows(rows)
    # return response


    file_name = f"{experiment.abbreviation}-{timestr}.csv"

    # Use StringIO for in-memory CSV content
    csv_buffer = StringIO()
    if level == constants.EXP_CSV_TYPE_FAMILY:
        headers = headers_arr + [unknown_species] + sorted(family_data.keys())
    else:
        headers = headers_arr + [unknown_species] + sorted(list(all_species))
    writer = csv.DictWriter(csv_buffer, headers, 0)
    writer.writeheader()
    if level != constants.EXP_CSV_TYPE_FAMILY:
        writer.writerows(morpho_headers)
    writer.writerows(rows)

    # Save the CSV content to the storage
    csv_content = csv_buffer.getvalue()
    csv_buffer.close()

    experiment.last_exported_file = ContentFile(csv_content, name=file_name)
    experiment.exported_file_status = 'success'
    experiment.save()

    return experiment.last_exported_file.url
