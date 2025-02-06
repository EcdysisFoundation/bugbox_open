import csv
import time
from datetime import datetime, timezone
from tempfile import SpooledTemporaryFile

from django.conf import settings
from django.contrib.auth.decorators import permission_required
from django.core.files import File
from django.db.models import Case, CharField, F, Func, Value, When
from django.http import Http404, HttpResponse

from ..core.models import Exports
from ..core.permissions import IS_RESEARCH
from ..taxonomy import constants as constants_tax
from ..taxonomy.models import Morphospecies
from ..taxonomy.utils import get_skip_morphospecies_ids
from . import constants
from .calculations import get_indices
from .models import Experiment, Sample, Site, Specimen, SpecimenImage


@permission_required(IS_RESEARCH)
def experiment_ai_csv(request, id):
    # get query params and sanitize
    try:
        experiment = Experiment.objects.user_access(request.user).get(id=id)
    except Experiment.DoesNotExist:
        raise Http404

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
    specimens = Specimen.objects.user_access(request.user).filter(
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
    try:
        experiment = Experiment.objects.user_access(request.user).get(id=id)
    except Experiment.DoesNotExist:
        raise Http404

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
        try:
            this_experiment = Experiment.objects.user_access(request.user).get(id=exp_id)
        except Experiment.DoesNotExist:
            raise Http404
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


PUBLIC_IMAGES_EXPORT_TITLE = 'public-images-exp'


def public_images_export(org_id):
    """
    Make an export file of public images, save the record in the db.
    """
    if not isinstance(org_id, int):
        raise TypeError('public_images_export only accepts integers for the org_id')
    # make filename
    now = datetime.now(tz=timezone.utc)
    filename = '__'.join([PUBLIC_IMAGES_EXPORT_TITLE, str(org_id),
                          now.strftime('%Y-%m-%d_%H%M%S')])
    filename = '%s.csv' % filename

    # headers and values query columns are the same
    export_headers = ['id', 'specimen_id', constants.SPECIMEN_IMAGE_IMAGE_THUMBNAIL_LARGE]
    export_headers = ['specimen__' +
                      v for v in [constants.FIELD_SPECIMEN_ARCHIVAL_IDENTIFIER,
                                  constants.FIELD_SPECIMEN_ARCHIVAL_STORED]]
    export_headers += ['specimen__sample__site_visit__' +
                       v for v in [constants.FIELD_SITE_VISIT_DATE]]
    export_headers += ['specimen__sample__site_visit__site__' +
                       v for v in [constants.FIELD_SITE_COUNTRY,
                                   constants.FIELD_SITE_STATE_REGION,
                                   constants.FIELD_SITE_COUNTY_REGION,
                                   constants.FIELD_SITE_US_STATE_COUNTY_FIPS]]
    export_headers += ['specimen__classification__' +
                       v for v in [constants_tax.FIELD_MORPHO_GBIF_CANONICAL_NAME,
                                   constants_tax.FIELD_MORPHO_GBIF_ORDER,
                                   constants_tax.FIELD_MORPHO_GBIF_FAMILY,
                                   constants_tax.FIELD_MORPHO_GBIF_GENUS,
                                   constants_tax.FIELD_MORPHO_GBIF_SPECIES,
                                   constants_tax.FIELD_MORPHO_GBIF_RANK]]
    # query data
    data = SpecimenImage.objects.filter(
        specimen__sample__site_visit__site__experiment__organization_id=org_id,
        public_image=True)
    data = data.values(*export_headers)

    specimens = set()
    orders = set()
    families = set()
    to_genera = 0
    to_species = 0

    max_mem_size = 5 * (2**20)  # max memory size before it writes to disk
    with SpooledTemporaryFile(mode='w+', newline='', max_size=max_mem_size) as tmpfile:
        writer = csv.writer(tmpfile)
        writer.writerow(export_headers + ['public_url'])
        for i in data:
            specimens.add(i['specimen_id'])
            orders.add(i['specimen__classification__' + constants_tax.FIELD_MORPHO_GBIF_ORDER])
            families.add(i['specimen__classification__' + constants_tax.FIELD_MORPHO_GBIF_FAMILY])
            if i['specimen__classification__' +
                 constants_tax.FIELD_MORPHO_GBIF_RANK] == constants_tax.GBIF_RANK_GENUS:
                to_genera += 1
            if i['specimen__classification__' +
                 constants_tax.FIELD_MORPHO_GBIF_RANK] == constants_tax.GBIF_RANK_SPECIES:
                to_species += 1
            url = settings.MEDIA_URL + i[constants.SPECIMEN_IMAGE_IMAGE_THUMBNAIL_LARGE]
            writer.writerow([str(i[v]) for v in export_headers] + [url])
        file_obj = File(tmpfile, name=filename)

        description = {
            'image_count': len(data),
            'specimen_count': len(specimens),
            'order_count': len(orders),
            'family_count': len(families),
            'identified_to_genus':  to_genera,
            'identified_to_species': to_species,
        }

        Exports.objects.create(
            organization_id=org_id,
            title=PUBLIC_IMAGES_EXPORT_TITLE,
            file=file_obj,
            description=description
        )
    # return the filename only
    return filename
