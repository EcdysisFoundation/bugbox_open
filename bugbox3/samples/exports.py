import csv
import time
from tempfile import SpooledTemporaryFile

from django.conf import settings
from django.contrib.auth.decorators import permission_required
from django.core.files import File
from django.db.models import Case, CharField, F, Func, Value, When
from django.http import Http404, HttpResponse
from django.shortcuts import redirect

from ..core.models import Exports
from ..core.permissions import IS_RESEARCH
from ..libs.utilities import get_filename_org_timestamp
from ..taxonomy import constants as constants_tax
from . import constants
from .models import Experiment, Specimen, SpecimenImage, UserExperimentFile
from .tasks import export_csv


@permission_required(IS_RESEARCH)
def experiment_ai_csv(request, id):
    # get query params and sanitize
    try:
        experiment = Experiment.objects.user_access(request.user).get(id=id)
    except Experiment.DoesNotExist:
        raise Http404

    sample_types = request.GET.getlist('sampleTypes')
    sites = request.GET.getlist('sites')
    other_experiments = request.GET.getlist('otherExperiments')

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
    if request.method == 'POST':
        try:
            experiment = Experiment.objects.user_access(request.user).get(id=id)
        except Experiment.DoesNotExist:
            raise Http404

        user_experiment_file, created = UserExperimentFile.objects.get_or_create(
            user=request.user,
            experiment=experiment
        )

        user_experiment_file.exported_file_status = 'pending'
        user_experiment_file.save()
        indices = request.POST.getlist('indices')
        # include abundance and species_richness first.
        indices = constants.INDICES_ALWAYS_INCLUDED + \
            [idx for idx in indices if idx not in constants.INDICES_ALWAYS_INCLUDED]
        # Expand "Hill Numbers" into its four components
        if 'hill_numbers' in indices:
            indices.remove('hill_numbers')
            indices.extend(['hill_H0', 'hill_H1', 'hill_H2', 'hill_inf'])
        print("Indices being processed in export_csv:", indices)
        export_type = request.POST.get('export-type')
        sample_types = request.POST.getlist('sampleTypes2')
        include_skip_morph = request.POST.get('include_skip_morph')
        sites = request.POST.getlist('sites2')
        other_experiments = request.POST.getlist('otherExperiments2')
        level = request.POST.get('level', 'morphospecies')

        export_csv.delay(
            request.user.pk,
            id,
            indices,
            export_type,
            sample_types,
            include_skip_morph,
            sites,
            other_experiments,
            level
        )

        return redirect('samples:experiment', experiment_id=id)

    raise Http404


PUBLIC_IMAGES_EXPORT_TITLE = 'public-reviewed-img-exp'
PUBLIC_ALL_IMAGES_EXPORT_TITLE = 'public-all-img-exp'


def get_public_export_headers(classification=constants.FIELD_SPECIMEN_CLASSIFICATION):
    c = classification
    if c not in (constants.FIELD_SPECIMEN_CLASSIFICATION, constants.FIELD_SPECIMEN_AI_CLASSIFICATION):
        return None
    query_fields = ['id', 'specimen_id', constants.SPECIMEN_IMAGE_IMAGE_THUMBNAIL_LARGE]
    query_fields += ['specimen__' +
                     v for v in [constants.FIELD_SPECIMEN_ARCHIVAL_IDENTIFIER,
                                 constants.FIELD_SPECIMEN_ARCHIVAL_STORED]]
    query_fields += ['specimen__sample__site_visit__' +
                     v for v in [constants.FIELD_SITE_VISIT_DATE]]
    query_fields += ['specimen__sample__site_visit__site__' +
                     v for v in [constants.FIELD_SITE_COUNTRY,
                                 constants.FIELD_SITE_STATE_REGION,
                                 constants.FIELD_SITE_COUNTY_REGION,
                                 constants.FIELD_SITE_US_STATE_COUNTY_FIPS]]
    query_fields += ['specimen__' + c + '__' +
                     v for v in [constants_tax.FIELD_MORPHO_GBIF_ORDER,
                                 constants_tax.FIELD_MORPHO_GBIF_FAMILY,
                                 constants_tax.FIELD_MORPHO_GBIF_GENUS,
                                 constants_tax.FIELD_MORPHO_GBIF_SPECIES]]

    out_headers = query_fields
    out_headers = [v.replace('specimen__' + c + '__', '') for v in out_headers]
    out_headers = [v.replace('specimen__sample__site_visit__site__', '') for v in out_headers]
    out_headers = [v.replace('specimen__sample__site_visit__', '') for v in out_headers]
    out_headers = [v.replace('specimen__', '') for v in out_headers]

    return {
        'query_fields': query_fields,
        'out_headers': out_headers
    }


def public_reviewed_images_q(org_id, query_fields):
    return SpecimenImage.objects.filter(
        specimen__sample__site_visit__site__experiment__organization_id=org_id,
        specimen__classification_id__isnull=False,
        public_image=True).exclude(specimen__acceptance=0).values(*query_fields)


def public_reviewed_img_export(org_id):
    """
    Make an export file of public images, save the record in the db.
    """
    if not isinstance(org_id, int):
        raise TypeError('public_images_export only accepts integers for the org_id')

    filename = get_filename_org_timestamp(PUBLIC_IMAGES_EXPORT_TITLE, org_id, 'csv')
    headers = get_public_export_headers(constants.FIELD_SPECIMEN_CLASSIFICATION)
    data = public_reviewed_images_q(org_id, headers['query_fields'])

    specimens = set()
    orders = set()
    families = set()

    max_mem_size = 5 * (2**20)  # max memory size before it writes to disk
    with SpooledTemporaryFile(mode='w+', newline='', max_size=max_mem_size) as tmpfile:
        writer = csv.writer(tmpfile)
        writer.writerow(headers['out_headers'] + ['reviewed', 'public_url'])
        for i in data:
            specimens.add(i['specimen_id'])
            orders.add(i['specimen__classification__' + constants_tax.FIELD_MORPHO_GBIF_ORDER])
            families.add(i['specimen__classification__' + constants_tax.FIELD_MORPHO_GBIF_FAMILY])
            url = settings.MEDIA_URL + i[constants.SPECIMEN_IMAGE_IMAGE_THUMBNAIL_LARGE]
            writer.writerow([str(i[v]) for v in headers['query_fields']] + ['True', url])
        file_obj = File(tmpfile, name=filename)

        description = {
            'image_count': len(data),
            'specimen_count': len(specimens),
            'order_count': len(orders),
            'family_count': len(families),
        }

        Exports.objects.create(
            organization_id=org_id,
            title=PUBLIC_IMAGES_EXPORT_TITLE,
            file=file_obj,
            description=description
        )
    # return the filename only
    return filename


def public_all_img_export(org_id):
    if not isinstance(org_id, int):
        raise TypeError('public_images_export only accepts integers for the org_id')
    # make filename
    filename = get_filename_org_timestamp(PUBLIC_ALL_IMAGES_EXPORT_TITLE, org_id, 'csv')
    headers = get_public_export_headers(constants.FIELD_SPECIMEN_AI_CLASSIFICATION)
    data = SpecimenImage.objects.filter(
        specimen__sample__site_visit__site__experiment__organization_id=org_id,
        specimen__ai_classification_id__isnull=False,
        specimen__acceptance=0,
        public_image=True
        ).values(*headers['query_fields'])

    reviwed_headers = get_public_export_headers(constants.FIELD_SPECIMEN_CLASSIFICATION)
    reviewed_data = public_reviewed_images_q(org_id, reviwed_headers['query_fields'])

    specimens = set()
    orders = set()
    families = set()

    max_mem_size = 5 * (2**20)  # max memory size before it writes to disk
    with SpooledTemporaryFile(mode='w+', newline='', max_size=max_mem_size) as tmpfile:
        writer = csv.writer(tmpfile)
        # adding to out_headers, if reviewed and the public url
        writer.writerow(headers['out_headers'] + ['reviewed', 'public_url'])
        # first enter the reviewed images, setting reviewed column to True
        for i in reviewed_data:
            specimens.add(i['specimen_id'])
            orders.add(i['specimen__classification__' + constants_tax.FIELD_MORPHO_GBIF_ORDER])
            families.add(i['specimen__classification__' + constants_tax.FIELD_MORPHO_GBIF_FAMILY])
            url = settings.MEDIA_URL + i[constants.SPECIMEN_IMAGE_IMAGE_THUMBNAIL_LARGE]
            writer.writerow([str(i[v]) for v in reviwed_headers['query_fields']] + ['True', url])
        # next, include all the unreviewed ones, setting reviewed column to False
        for i in data:
            specimens.add(i['specimen_id'])
            orders.add(i['specimen__ai_classification__' + constants_tax.FIELD_MORPHO_GBIF_ORDER])
            families.add(i['specimen__ai_classification__' + constants_tax.FIELD_MORPHO_GBIF_FAMILY])
            url = settings.MEDIA_URL + i[constants.SPECIMEN_IMAGE_IMAGE_THUMBNAIL_LARGE]
            # redact genus and species on these
            i['specimen__ai_classification__' + constants_tax.FIELD_MORPHO_GBIF_GENUS] = ''
            i['specimen__ai_classification__' + constants_tax.FIELD_MORPHO_GBIF_SPECIES] = ''
            writer.writerow([str(i[v]) for v in headers['query_fields']] + ['False', url])
        file_obj = File(tmpfile, name=filename)

        description = {
            'image_count': len(data) + len(reviewed_data),
            'specimen_count': len(specimens),
            'order_count': len(orders),
            'family_count': len(families),
        }

        Exports.objects.create(
            organization_id=org_id,
            title=PUBLIC_ALL_IMAGES_EXPORT_TITLE,
            file=file_obj,
            description=description
        )
    # return the filename only
    return filename
