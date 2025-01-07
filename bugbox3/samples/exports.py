import csv
import time

from django.contrib.auth.decorators import permission_required
from django.db.models import Case, CharField, F, Func, Value, When
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from ..core.permissions import IS_RESEARCH
from ..taxonomy.models import Morphospecies
from ..taxonomy.utils import get_skip_morphospecies_ids
from . import constants
from .calculations import get_indices
from .models import Experiment, Sample, Site, Specimen


@permission_required(IS_RESEARCH)
def experiment_ai_csv(request, id):
    # get query params and sanitize
    experiment = get_object_or_404(Experiment, id=id)
    sample_types = request.GET.getlist('sampleTypes')
    sites = request.GET.getlist('sites')
    if not all([v.isnumeric() for v in sites]):
        return HttpResponse(status=404)
    sites = [int(v) for v in sites]
    other_experiments = request.GET.getlist('otherExperiments')
    if not all([v.isnumeric() for v in other_experiments]):
        return HttpResponse(status=404)
    other_experiments = [int(v) for v in other_experiments]
    all_exp = other_experiments + [experiment.id]
    headersArr = constants.EXPERIMENT_AI_CSV + ['Top 1 Correct', 'Top 3 Correct']
    specimens = Specimen.objects.filter(
        sample__site_visit__site__experiment_id__in=all_exp,
        sample__sample_type__in=sample_types).exclude(
            acceptance=constants.ACCEPTANCE_PENDING)
    if not other_experiments:
        specimens = specimens.filter(
            sample__site_visit__site__in=sites)
    else:
        specimens = specimens.order_by('sample__site_visit__site__experiment__name')
    specimens = specimens.values_list(
        *constants.EXPERIMENT_AI_CSV,
        Case(When(classification=F(constants.FIELD_SPECIMEN_AI_CLASSIFICATION), then=1),
             default=0, output_field=CharField()),
        Case(When(classification=F(constants.FIELD_SPECIMEN_AI_CLASSIFICATION), then=1),
             When(classification__name=Func(
                F(constants.FIELD_SPECIMEN_OPTIONAL_PRED_ONE),
                Value('class_op'),
                function='jsonb_extract_path_text',
             ), then=1),
             When(classification__name=Func(
                F(constants.FIELD_SPECIMEN_OPTIONAL_PRED_TWO),
                Value('class_op'),
                function='jsonb_extract_path_text',
             ), then=1),
             default=0, output_field=CharField())
    )
    timestr = time.strftime("%Y%m%d-%H%M%S")
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{0}-{1}.csv"'.format(
        experiment.abbreviation, timestr)
    writer = csv.writer(response)
    writer.writerow(headersArr)
    writer.writerows(list(specimens))
    return response


@permission_required(IS_RESEARCH)
def experiment_csv(request, id):
    # get query params and sanitize
    experiment = get_object_or_404(Experiment, id=id)
    indices = request.GET.getlist('indices')
    indices = [v for v in indices if v in constants.INDICES_CHOICES_ALL]
    export_type = request.GET.get('export-type')
    export_type = export_type if export_type in constants.EXPERIMENT_CSV_EXPORT_TYPES else None
    sample_types = request.GET.getlist('sampleTypes2')
    include_skip_morph = request.GET.get('include_skip_morph')
    sites = request.GET.getlist('sites2')
    if not all([v.isnumeric() for v in sites]):
        return HttpResponse(status=404)
    sites = [int(v) for v in sites]
    if not sites:
        sites = Site.objects.filter(experiment_id=experiment.id).values_list('id', flat=True)
    other_experiments = request.GET.getlist('otherExperiments2')
    if not all([v.isnumeric() for v in other_experiments]):
        return HttpResponse(status=404)
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
        this_experiment = get_object_or_404(Experiment, id=exp_id)
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
                if name in row.keys():
                    row[name] += total
                else:
                    row[name] = total
                n += 1 + specimen.partial_count
            if indices:
                indice_results = get_indices(n, row, headers_arr)
                for i in indices:
                    row[i] = indice_results[i]

            rows.append(row)
    timestr = time.strftime("%Y%m%d-%H%M%S")
    all_species.remove(unknown_species)  # moving unknown to the front
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{0}-{1}.csv"'.format(
        experiment.abbreviation, timestr)
    writer = csv.DictWriter(response, headers_arr + [unknown_species] + sorted(list(all_species)), 0)
    writer.writeheader()
    writer.writerows(morpho_headers)
    writer.writerows(rows)
    return response
