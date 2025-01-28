import csv
import time
from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.files.storage import default_storage
from django.db.models import Count, Q
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import CreateView, FormView, TemplateView, UpdateView
from rest_framework.reverse import reverse as api_reverse
from rest_framework.viewsets import ReadOnlyModelViewSet

from ..core.permissions import (ADD_MORPHOSPECIES, CHANGE_MORPHOSPECIES,
                                IS_RESEARCH)
from ..core.views import DatatablesModelViewSetMixin
from ..libs.ui_helpers import (calc_image_height, get_datatables_container,
                               get_datatables_row)
from ..libs.utilities import get_json_context, get_media_url
from ..samples import constants as samples_constants
from ..samples.models import Sample, Specimen, SpecimenImage
from . import constants
from .forms import (MorphospeciesCombineForm, MorphospeciesForm,
                    MorphospeciesUpdateForm)
from .models import AiTraining, Morphospecies
from .serializers import (MorphospeciesDatatablesSerializer,
                          MorphospeciesPickerSerializer)
from .tasks import id_image


class MorphospeciesDatatablesViewSet(PermissionRequiredMixin, DatatablesModelViewSetMixin, ReadOnlyModelViewSet):

    permission_required = IS_RESEARCH
    serializer_class = MorphospeciesDatatablesSerializer
    search_vector = (
        constants.FIELD_MORPHO_NAME,
        constants.FIELD_MORPHO_GBIF_CANONICAL_NAME
    )

    def get_queryset(self):
        gbif_rank = None
        first_check = None
        morphospecies = Morphospecies.objects.all()
        if self.request.query_params.get('first_filter'):
            gbif_rank = self.request.query_params.get('first_filter')
        if self.request.query_params.get('first_check'):
            first_check = self.request.query_params.get('first_check')
        if gbif_rank in constants.GBIF_RANK_VALUES:
            morphospecies = morphospecies.filter(gbif_rank=gbif_rank)
        if not first_check:
            morphospecies = morphospecies.exclude(defunt_date__isnull=False)
        return morphospecies.order_by(constants.FIELD_MORPHO_NAME)


class MorphospeciesPickerViewSet(PermissionRequiredMixin, DatatablesModelViewSetMixin, ReadOnlyModelViewSet):

    permission_required = IS_RESEARCH
    serializer_class = MorphospeciesPickerSerializer
    search_vector = (
        constants.FIELD_MORPHO_NAME,
        constants.FIELD_MORPHO_GBIF_CANONICAL_NAME
    )

    def get_queryset(self):
        if self.request.query_params.get('first_filter'):
            gbif_rank = self.request.query_params.get('first_filter')
            if gbif_rank in constants.GBIF_RANK_VALUES:
                return Morphospecies.objects.filter(gbif_rank=gbif_rank).order_by(constants.FIELD_MORPHO_NAME)
        return Morphospecies.objects.all().order_by(constants.FIELD_MORPHO_NAME)


class MophospeciesView(PermissionRequiredMixin, TemplateView):

    permission_required = IS_RESEARCH
    template_name = 'taxonomy/morphospecies.html'

    first_check_txt = 'Show defunct morphospecies'

    def get_morphospecies_datatable(self, datatables_url):
        """
        Forat the datatables context, including the url from rest_framework.reverse
        as datatables_url
        """
        return {
            'json_context': get_json_context({
                'datatables_url': datatables_url,
                'first_picker_choices': constants.GBIF_RANK_CHOICES_WO_BLANK_LIST,
                'first_picker_text': 'any rank',
                'first_check': self.first_check_txt
            }),
            'container_row_header': get_datatables_container(
                get_datatables_row([
                    'Name',
                    'Canonical Name',
                    'Rank'
                ])),
            }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        datatables_url = api_reverse('taxonomy:morphospecies-data-list',
                                     request=self.request, kwargs=kwargs)
        context.update(self.get_morphospecies_datatable(datatables_url))
        context.update({
            'can_add': self.request.user.has_perm(ADD_MORPHOSPECIES),
            'exp_morph_choices': constants.EXP_MORPH_CHOICES,
            'first_check': self.first_check_txt
        })
        return context


class MorphospeciesDetailView(PermissionRequiredMixin, FormView):

    form_class = MorphospeciesCombineForm
    permission_required = IS_RESEARCH
    template_name = 'taxonomy/morphospecies_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        morphospecies = get_object_or_404(Morphospecies, id=self.kwargs['id'])
        image_set = []
        if morphospecies.gbif_rank == constants.GBIF_RANK_SPECIES and morphospecies.gbif_canonical_name:
            display_name = morphospecies.gbif_canonical_name
        else:
            display_name = morphospecies.name
        image_count = SpecimenImage.objects.filter(
            specimen__classification=morphospecies,
            specimen__sample__site_visit__site__experiment__organization_id=samples_constants.ECDYSIS_ORGANIZATION_ID).aggregate(
            reviewed=Count(
                'pk', distinct=True, filter=~Q(
                    specimen__acceptance=samples_constants.ACCEPTANCE_PENDING)), pending=Count(
                        'pk', distinct=True, filter=Q(specimen__acceptance=samples_constants.ACCEPTANCE_PENDING)))
        sum_image_count = image_count['reviewed'] + image_count['pending']
        if sum_image_count:
            archive = 'specimen__' + samples_constants.FIELD_SPECIMEN_ARCHIVAL_IDENTIFIER
            s_images = SpecimenImage.objects.filter(
                specimen__classification=morphospecies,
                specimen__sample__site_visit__site__experiment__organization_id=samples_constants.ECDYSIS_ORGANIZATION_ID).order_by(
                archive, samples_constants.SPECIMEN_IMAGE_PRIMARY)[:2]
            max_width = samples_constants.SPECIMEN_IMAGE_THUMBSIZE_MEDIUM
            for s in s_images:
                if s.image_thumbnail_medium:
                    i = s.image_thumbnail_medium
                elif s.image_thumbnail:
                    i = s.image_thumbnail
                else:
                    i = s.image
                if default_storage.exists(i.name):
                    image_set.append({
                        'path': get_media_url(i, s.public_image),
                        'width': i.width if i.width <= max_width else max_width,
                        'height': i.height if i.width <= max_width else calc_image_height(max_width, i.height, i.width)
                    })
        img_thumbnail = None
        img = None
        if morphospecies.image_thumbnail:
            if default_storage.exists(morphospecies.image_thumbnail.name):
                img_thumbnail = {
                    'path': get_media_url(morphospecies.image_thumbnail),
                    'height': morphospecies.image_thumbnail.height,
                    'width': morphospecies.image_thumbnail.width
                }
        elif morphospecies.image:
            if default_storage.exists(morphospecies.image.name):
                img_thumbnail = {
                    'path': get_media_url(morphospecies.image),
                    'height': calc_image_height(
                        constants.MORPHPOSPECIES_THUMBSIZE,
                        morphospecies.image.height,
                        morphospecies.image.width
                    ),
                    'width': constants.MORPHPOSPECIES_THUMBSIZE
                }
        if morphospecies.image:
            if default_storage.exists(morphospecies.image.name):
                img = {
                    'path': get_media_url(morphospecies.image),
                    'height': morphospecies.image.height,
                    'width': morphospecies.image.width
                }
        ai = AiTraining.objects.filter(morphospecies=morphospecies).order_by('id').all()
        ai_accuracy_over_time = {
            'precision': [[a.entered_date, a.precision] for a in ai],
            'f1': [[a.entered_date, a.f1] for a in ai],
            'recall': [[a.entered_date, a.recall] for a in ai],
            'total': [a.train for a in ai]
        }
        context.update({
            'can_edit': self.request.user.has_perm(CHANGE_MORPHOSPECIES),
            'display_name': display_name,
            'morphospecies': morphospecies,
            'ai_last_train': ai_accuracy_over_time['total'][-1] if ai_accuracy_over_time['total'] else 0,
            'image_set': image_set,
            'image_count': image_count,
            'img_thumbnail': img_thumbnail,
            'img': img,
            'specimen_count': Specimen.objects.filter(classification=morphospecies).aggregate(
                reviewed=Count(
                    'pk', distinct=True,
                    filter=~Q(acceptance=samples_constants.ACCEPTANCE_PENDING)), pending=Count(
                        'pk', distinct=True, filter=Q(acceptance=samples_constants.ACCEPTANCE_PENDING))),
            'json_context': get_json_context({
                'ai_accuracy_over_time': ai_accuracy_over_time,
                'datatables_url': api_reverse('taxonomy:morphospecies-picker-list',
                                              request=self.request, kwargs=kwargs),
                'first_picker_choices': constants.GBIF_RANK_CHOICES_WO_BLANK_LIST,
                'first_picker_text': 'any rank',
            })
        })
        return context

    def form_valid(self, form):
        combine_to_id = form.cleaned_data['combine_to_id']
        if combine_to_id and self.request.user.has_perm(CHANGE_MORPHOSPECIES):
            morphospecies = get_object_or_404(Morphospecies, id=self.kwargs['id'])
            combine_to = get_object_or_404(Morphospecies, id=combine_to_id)

            if morphospecies.id != combine_to.id:
                if not morphospecies.defunt_date:
                    Specimen.objects.filter(classification=morphospecies).update(
                        classification_id=combine_to.id)
                    Specimen.objects.filter(ai_classification=morphospecies).update(
                        ai_classification_id=combine_to.id)
                    morphospecies.defunt_date = datetime.today()
                    morphospecies.defunt_user = self.request.user
                    morphospecies.defunt_morpho = combine_to
                    morphospecies.save()

                    messages.success(self.request, 'Successfully combined {0} (id={1}) to {2} (id={3})'.format(
                        morphospecies.name, morphospecies.id, combine_to.name, combine_to.id))
                else:
                    messages.warning(
                        self.request, 'Warning: {0} (id={3}) is a defunct Morphospecies, did not save changes').format(
                        combine_to.name, combine_to.id
                    )
            else:
                messages.warning(
                    self.request, 'Warning: {0} (id={1}) is the same as {2} (id={3}), did not save changes'.format(
                        morphospecies.name, morphospecies.id, combine_to.name, combine_to.id))
        return super().form_valid(form)

    def get_success_url(self):
        if self.request.POST['combine_to_id']:
            return reverse(
                'taxonomy:morphospecies'
            )
        return reverse('taxonomy:morphospecies-detail', kwargs={'id': self.kwargs['id']})


class MorphospeciesCreateView(PermissionRequiredMixin, CreateView):

    permission_required = IS_RESEARCH + [ADD_MORPHOSPECIES]
    form_class = MorphospeciesForm
    template_name = 'taxonomy/morphospecies_form.html'
    action = 'create'

    def get_context_data(self, **kwargs):
        context = super(MorphospeciesCreateView, self).get_context_data(**kwargs)
        context.update({'json_context': get_json_context({
            'action': self.action
        })})
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Succesfully created a Morphospecies')
        return super(MorphospeciesCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('taxonomy:morphospecies-detail', kwargs={'id': self.object.id})


class MorphospeciesUpdateView(PermissionRequiredMixin, UpdateView):

    permission_required = IS_RESEARCH + [CHANGE_MORPHOSPECIES]
    form_class = MorphospeciesUpdateForm
    template_name = 'taxonomy/morphospecies_form_update.html'
    action = 'update'

    def get_object(self, queryset=None):
        return get_object_or_404(Morphospecies, id=self.kwargs['id'])

    def get_context_data(self, **kwargs):
        context = super(MorphospeciesUpdateView, self).get_context_data(**kwargs)
        context.update({'json_context': get_json_context({
            'action': self.action
        })})
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Succesfully updated a Morphospecies')
        return super(MorphospeciesUpdateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('taxonomy:morphospecies-detail', kwargs={'id': self.object.id})


@permission_required(IS_RESEARCH)
def classify_specimen(request, id):
    if not settings.AI_INFERENCE_URL:
        return Http404('The AI_INFERENCE_URL is not avaialble')
    id_image.delay(id)
    time.sleep(2)
    return redirect(request.META['HTTP_REFERER'])


@permission_required(IS_RESEARCH)
def classify_sample(request, id):
    if not settings.AI_INFERENCE_URL:
        return Http404('The AI_INFERENCE_URL is not avaialble')
    try:
        sample = Sample.objects.user_access(request.user).get(id=id)
    except Sample.DoesNotExist:
        raise Http404
    specimen = Specimen.objects.filter(sample=sample, acceptance=0)
    for s in specimen:
        id_image.delay(s.id)
    time.sleep(3)
    return redirect(request.META['HTTP_REFERER'])


@permission_required(IS_RESEARCH)
def morphospecies_csv(request):
    response = HttpResponse(content_type='text/csv')
    name = request.GET.get('name')
    name = name if name in constants.EXP_MORPH_CHOICES_NAMES else ''
    headers = ['None']
    result_values_list = []

    if name == constants.EXP_MORPH_ALL_MORPH:
        headers = constants.EXPORT_HEADERS_MORPHOSPECIES
        result_values_list = Morphospecies.objects.values_list(*headers)
    timestr = time.strftime("%Y%m%d-%H%M%S")
    response['Content-Disposition'] = 'attachment; filename="{0}-{1}.csv"'.format(
        name, timestr)
    writer = csv.writer(response)
    writer.writerow(headers)
    writer.writerows(list(result_values_list))

    return response
