from time import sleep

from django.contrib import messages
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import CreateView, TemplateView
from rest_framework.reverse import reverse as api_reverse
from rest_framework.viewsets import ReadOnlyModelViewSet

from ..core.views import DatatablesModelViewSetMixin
from ..libs.ui_helpers import calc_image_height, get_datatables_container, get_datatables_row
from ..libs.utilities import get_json_context
from ..samples import constants as samples_constants
from ..samples.models import Sample, Specimen, SpecimenImage
from . import constants
from .forms import MorphospeciesForm
from .models import AiTraining, Morphospecies
from .serializers import MorphospeciesDatatablesSerializer
from .tasks import id_image


class MorphospeciesDatatablesViewSet(DatatablesModelViewSetMixin, ReadOnlyModelViewSet):
    serializer_class = MorphospeciesDatatablesSerializer
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


class MophospeciesView(TemplateView):
    template_name = 'taxonomy/morphospecies.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        datatables_url = api_reverse('taxonomy:morphospecies-data-list',
                                     request=self.request, kwargs=kwargs)
        context.update({
            'json_context': get_json_context({
                'datatables_url': datatables_url,
                'first_picker_choices': constants.GBIF_RANK_CHOICES_WO_BLANK_LIST,
                'first_picker_text': 'any rank'
            }),
            'container_row_header': get_datatables_container(
                get_datatables_row([
                    'Name',
                    'Canonical Name',
                    'Rank'
                ])),
        })
        return context


class MorphospeciesDetailView(TemplateView):
    template_name = 'taxonomy/morphospecies_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        morphospecies = get_object_or_404(
            Morphospecies.objects.all(), id=kwargs['id'])
        image_set = []
        if morphospecies.gbif_rank == constants.GBIF_RANK_SPECIES and morphospecies.gbif_canonical_name:
            display_name = morphospecies.gbif_canonical_name
        else:
            display_name = morphospecies.name
        image_count = SpecimenImage.objects.filter(specimen__classification=morphospecies).aggregate(
            reviewed=Count(
                'pk', distinct=True, filter=~Q(
                    specimen__acceptance=samples_constants.ACCEPTANCE_PENDING)), pending=Count(
                        'pk', distinct=True, filter=Q(specimen__acceptance=samples_constants.ACCEPTANCE_PENDING)))
        sum_image_count = image_count['reviewed'] + image_count['pending']
        if sum_image_count:
            archive = 'specimen__' + samples_constants.FIELD_SPECIMEN_ARCHIVAL_IDENTIFIER
            s_images = SpecimenImage.objects.filter(specimen__classification=morphospecies).order_by(
                archive, samples_constants.SPECIMEN_IMAGE_PRIMARY)[:2]
            max_width = samples_constants.SPECIMEN_IMAGE_THUMBSIZE_MEDIUM
            for s in s_images:
                if s.image_thumbnail_medium:
                    i = s.image_thumbnail_medium
                elif s.image_thumbnail:
                    i = s.image_thumbnail
                else:
                    i = s.image
                image_set.append({
                    'path': i.url,
                    'width': i.width if i.width <= max_width else max_width,
                    'height': i.height if i.width <= max_width else calc_image_height(max_width, i.height, i.width)
                })

        ai = AiTraining.objects.filter(morphospecies=morphospecies).select_related('model').order_by('id').all()
        ai_accuracy_over_time = {
            'precision': [[a.model.entered_date, a.precision] for a in ai],
            'f1': [[a.model.entered_date, a.f1] for a in ai],
            'recall': [[a.model.entered_date, a.recall] for a in ai],
            'train': [a.train for a in ai]
        }
        context.update({
            'display_name': display_name,
            'morphospecies': morphospecies,
            'ai_last_train': ai_accuracy_over_time['train'][-1] if ai_accuracy_over_time['train'] else 0,
            'image_set': image_set,
            'image_count': image_count,
            'specimen_count': Specimen.objects.filter(classification=morphospecies).aggregate(
                reviewed=Count(
                    'pk', distinct=True,
                    filter=~Q(acceptance=samples_constants.ACCEPTANCE_PENDING)), pending=Count(
                        'pk', distinct=True, filter=Q(acceptance=samples_constants.ACCEPTANCE_PENDING))),
            'json_context': get_json_context({
                'ai_accuracy_over_time': ai_accuracy_over_time
            })
        })
        return context


class MorphospeciesCreateView(CreateView):

    form_class = MorphospeciesForm
    template_name = 'taxonomy/morphospecies_form.html'
    action = 'create'

    def get_context_data(self, **kwargs):
        context = super(MorphospeciesCreateView, self).get_context_data(**kwargs)
        context.update({
            'gbif': 'Search GBIF',
            'json_context': {
                'GBIF_DATASET': 'd7dddbf4-2cf0-4f39-9b2a-bb099caae36c',
                'query_params': ['q']
            }
        })
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Succesfully created a Morphospecies')
        return super(MorphospeciesCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('taxonomy:morphospecies-detail', kwargs={'id': self.object.id})


def classify_specimen(request, id):
    id_image.delay(id)
    sleep(2)
    return redirect(request.META['HTTP_REFERER'])


def classify_sample(request, id):
    sample = get_object_or_404(Sample, id=id)
    specimen = Specimen.objects.filter(sample=sample, acceptance=0)
    for s in specimen:
        id_image.delay(s.id)
    sleep(3)
    return redirect(request.META['HTTP_REFERER'])
