import csv
import time
from datetime import datetime, timezone
from tempfile import SpooledTemporaryFile

from django.conf import settings
from django.contrib.auth.decorators import permission_required
from django.core.files import File
from django.db.models import Case, CharField, F, Func, Value, When
from django.http import Http404, HttpResponse
from django.shortcuts import redirect

from ..core.models import Exports
from ..core.permissions import IS_RESEARCH
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
        indices = constants.INDICES_ALWAYS_INCLUDED + [idx for idx in indices if idx not in constants.INDICES_ALWAYS_INCLUDED]
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
    export_headers += ['specimen__' +
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
