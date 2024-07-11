import csv
import time

from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db import transaction
from django.db.models import Case, CharField, F, Func, Value, When
from django.forms import inlineformset_factory
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, DeleteView, FormView, UpdateView
from rest_framework.reverse import reverse as api_reverse
from rest_framework.viewsets import ReadOnlyModelViewSet

from ..core.permissions import IS_RESEARCH, REVIEW_SPECIMEN_PAGE
from ..core.views import DatatablesModelViewSetMixin
from ..libs.ui_helpers import (
    calc_image_height,
    get_datatables_container,
    get_datatables_row,
    get_formsets_display_control_config,
    get_probability,
)
from ..libs.utilities import get_json_context
from ..taxonomy.constants import GBIF_RANK_CHOICES_WO_BLANK_LIST
from ..taxonomy.models import Morphospecies
from . import constants
from .calculations import get_indices
from .forms import (
    ExperimentForm,
    JSONFieldForm,
    NewSpecimenImageForm,
    SampleForm,
    SamplePlanForm,
    SiteForm,
    SiteVisitForm,
    SpecimenForm,
    SpecimenViewForm,
)
from .models import Experiment, Sample, SamplePlan, Site, SiteVisit, Specimen, SpecimenImage
from .models_query import get_sample_plan_descriptions
from .serializers import (
    ExperimentsDatatablesSerializer,
    SamplesDatatablesSerializer,
    SitesDatatablesSerializer,
    SpecimenDatatablesSerializer,
    SpecimensAllDatatablesSerializer,
)


class ExperimentsDatatablesViewSet(PermissionRequiredMixin, DatatablesModelViewSetMixin, ReadOnlyModelViewSet):

    permission_required = IS_RESEARCH

    serializer_class = ExperimentsDatatablesSerializer
    queryset = Experiment.objects.all().order_by(constants.FIELD_NAME)
    search_vector = [constants.FIELD_NAME, constants.FIELD_ABBREVIATION]


class SamplesDatatablesViewSet(PermissionRequiredMixin, DatatablesModelViewSetMixin, ReadOnlyModelViewSet):

    permission_required = IS_RESEARCH

    serializer_class = SamplesDatatablesSerializer
    search_vector = [constants.FIELD_SAMPLE_TYPE]

    def get_queryset(self):
        experiment_id = int(self.kwargs['experiment_id'])
        return Sample.objects.filter(site_visit__site__experiment_id=experiment_id)


class SitesDatatablesViewSet(PermissionRequiredMixin, DatatablesModelViewSetMixin, ReadOnlyModelViewSet):

    permission_required = IS_RESEARCH

    serializer_class = SitesDatatablesSerializer
    search_vector = [
            constants.FIELD_SITE_SITE_NAME,
            constants.FIELD_SITE_STATE_REGION,
            constants.FIELD_SITE_HABITAT_TYPE,
            constants.FIELD_SITE_TREATMENT
        ]

    def get_queryset(self):
        experiment_id = int(self.kwargs['experiment_id'])
        return Site.objects.filter(experiment_id=experiment_id)


class SpecimenDatatablesViewSet(PermissionRequiredMixin, DatatablesModelViewSetMixin, ReadOnlyModelViewSet):

    permission_required = IS_RESEARCH

    serializer_class = SpecimenDatatablesSerializer
    search_vector = ['classification__name']

    def get_queryset(self):
        sample_id = int(self.kwargs['sample_id'])
        return Specimen.objects.filter(sample_id=sample_id).order_by('-id')


class SpecimensAllDatatablesViewSet(PermissionRequiredMixin, DatatablesModelViewSetMixin, ReadOnlyModelViewSet):

    permission_required = IS_RESEARCH

    serializer_class = SpecimensAllDatatablesSerializer
    search_vector = [
        'classification__name',
        'ai_classification__name',
    ]

    def get_queryset(self):
        specimen = Specimen.objects.filter(
            sample__site_visit__site__experiment__isnull=False
        )
        id = int(self.kwargs['id'])
        sample_id = int(self.kwargs['sample_id'])
        if id and not sample_id:
            specimen = specimen.filter(sample__site_visit__site__experiment__id=id)
        elif id and sample_id:
            specimen = specimen.filter(
                sample__site_visit__site__experiment__id=id,
                sample__id=sample_id,
            )
        if self.request.query_params.get('acceptance_filter'):
            acceptance = self.request.query_params.get('acceptance_filter')
            specimen = specimen.filter(acceptance=acceptance)
        if self.request.query_params.get('class_filter'):
            if self.request.query_params.get('class_filter'):
                specimen = specimen.filter(classification_id__isnull=True)
        return specimen.order_by('-id')


class ExperimentsView(PermissionRequiredMixin, TemplateView):

    permission_required = IS_RESEARCH

    template_name = 'samples/experiments.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        experiments_datatables_url = api_reverse('samples:experiment-data-list',
                                                 request=self.request, kwargs=kwargs)
        context.update({
            'json_context': get_json_context({'experiments_datatables_url': experiments_datatables_url}),
            'container_row_header': get_datatables_container(
                get_datatables_row([
                    'Experiment',
                    'Abbreviation',
                    'Year/s',
                    'Samples',
                    'Photosampling Needed',
                    'Reviewed Needed'
                ])),
        })
        return context


class ExperimentView(PermissionRequiredMixin, TemplateView):

    permission_required = IS_RESEARCH

    template_name = 'samples/experiment.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        experiment = get_object_or_404(Experiment.objects.all(), id=kwargs['experiment_id'])
        if experiment.from_year == experiment.to_year:
            years = str(experiment.from_year)
        else:
            years = str(experiment.from_year) + ' - ' + str(experiment.to_year)
        description = [v['description'] for v in get_sample_plan_descriptions(experiment.id)]
        sites_datatables_url = api_reverse(
            'samples:site-data-list', request=self.request, kwargs=kwargs)
        experiment_sites = Site.objects.filter(
            experiment_id=experiment.id).order_by(
                constants.FIELD_SITE_SITE_NAME)
        other_experiments = Experiment.objects.exclude(
            id=experiment.id).order_by(constants.FIELD_ABBREVIATION)
        context.update({
            'experiment': experiment,
            'experiment_sites': experiment_sites,
            'other_experiments': other_experiments,
            'sample_types': constants.SAMPLE_TYPE_CHOICES,
            'indices': constants.INDICES_CHOICES,
            'export_types': constants.EXPERIMENT_CSV_EXPORT_CHOICES,
            'years': years,
            'sample_plan_descriptions': description,
            'review_permission': self.request.user.has_perm(REVIEW_SPECIMEN_PAGE),
            'container_row_header': get_datatables_container(
                get_datatables_row([
                    'Site Name',
                    'State Region',
                    'County Region',
                    'Habitat',
                    'Treatment'
                ])),
            'json_context': get_json_context(
                {'sites_datatables_url': sites_datatables_url})
        })
        return context


class ExperimentSamplePlanCreateView(PermissionRequiredMixin, CreateView):

    permission_required = IS_RESEARCH

    form_class = ExperimentForm
    template_name = 'samples/experiment_form.html'
    action = 'create'

    formset_total = 10
    formset_intial = 1

    sample_plan_form_set = inlineformset_factory(
        Experiment, SamplePlan, form=SamplePlanForm, max_num=formset_total, extra=formset_total)

    def get_context_data(self, **kwargs):
        context = super(ExperimentSamplePlanCreateView, self).get_context_data(**kwargs)
        context['json_context'] = get_json_context(get_formsets_display_control_config(
                    self.formset_total, self.formset_intial))
        context['form_action_url'] = reverse('samples:experiment-sample-plan-create')
        if self.request.POST:
            context['formsets'] = self.sample_plan_form_set(self.request.POST)
        else:
            context['formsets'] = self.sample_plan_form_set()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formsets = context['formsets']
        with transaction.atomic():
            self.object = form.save()
            if formsets.is_valid():
                formsets.instance = self.object
                formsets.save()
            else:
                print('ERRORS_formsets: ' + str(formsets.errors))
        return super(ExperimentSamplePlanCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('samples:experiments')


class ExperimentSamplePlanUpdateView(PermissionRequiredMixin, UpdateView):

    permission_required = IS_RESEARCH

    form_class = ExperimentForm
    template_name = 'samples/experiment_form.html'
    action = 'update'

    formset_total = 10

    sample_plan_form_set = inlineformset_factory(
        Experiment, SamplePlan, form=SamplePlanForm, max_num=formset_total, extra=formset_total,
        can_delete=True)

    def get_object(self, queryset=None):
        return get_object_or_404(Experiment, id=self.kwargs['experiment_id'])

    def get_context_data(self, **kwargs):
        context = super(ExperimentSamplePlanUpdateView, self).get_context_data(**kwargs)
        sample_plan_count = SamplePlan.objects.filter(experiment_id=self.object.id).count()
        if sample_plan_count < 1:
            sample_plan_count = 1
        context['json_context'] = get_json_context(get_formsets_display_control_config(
                    self.formset_total, sample_plan_count))
        context['form_action_url'] = reverse('samples:experiment-sample-plan-update',
                                             kwargs={'experiment_id': self.kwargs['experiment_id']})
        if self.request.POST:
            context['formsets'] = self.sample_plan_form_set(self.request.POST, instance=self.object)
        else:
            context['formsets'] = self.sample_plan_form_set(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formsets = context['formsets']
        with transaction.atomic():
            self.object = form.save()
            if formsets.is_valid():
                formsets.instance = self.object
                formsets.save()
            else:
                print('ERRORS_formsets: ' + str(formsets.errors))
        return super(ExperimentSamplePlanUpdateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('samples:experiments')


class SiteCreateView(PermissionRequiredMixin, CreateView):

    permission_required = IS_RESEARCH

    form_class = SiteForm
    template_name = 'samples/site_form.html'
    action = 'create'

    formset_total = 10

    form_set = inlineformset_factory(Site, SiteVisit, form=SiteVisitForm, max_num=formset_total, extra=formset_total)

    def get_context_data(self, **kwargs):
        context = super(SiteCreateView, self).get_context_data(**kwargs)
        experiment = get_object_or_404(Experiment, id=self.kwargs['experiment_id'])
        context['experiment_details'] = {
            'experiment': experiment,
            'plans': get_sample_plan_descriptions(experiment.id)
        }
        context['json_context'] = get_json_context(get_formsets_display_control_config(
                    self.formset_total, experiment.date_per_site))
        context['form_action_url'] = reverse(
            'samples:site-create', kwargs={'experiment_id': self.kwargs['experiment_id']})
        self.experiment = experiment
        if self.request.POST:
            context['formsets'] = self.form_set(self.request.POST)
        else:
            context['formsets'] = self.form_set()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        form.instance.experiment_id = context['experiment_details']['experiment'].id
        formsets = context['formsets']
        self.object = form.save()
        if formsets.is_valid():
            formsets.instance = self.object
            instances = formsets.save(commit=False)
            for i in instances:
                i.created_by_user_id = self.request.user.id
                i.save()
            formsets.save()
        else:
            print('ERRORS_formsets: ' + str(formsets.errors))
        return super(SiteCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('samples:experiment', kwargs={'experiment_id': self.kwargs['experiment_id']})


class SiteUpdateView(PermissionRequiredMixin, UpdateView):

    permission_required = IS_RESEARCH

    form_class = SiteForm
    template_name = 'samples/site_form.html'
    action = 'update'

    formset_total = 20

    form_set = inlineformset_factory(Site, SiteVisit, form=SiteVisitForm, max_num=formset_total, extra=formset_total)

    def get_object(self, queryset=None):
        return get_object_or_404(Site, id=self.kwargs['site_id'])

    def get_context_data(self, **kwargs):
        context = super(SiteUpdateView, self).get_context_data(**kwargs)
        experiment = get_object_or_404(Experiment, id=self.object.experiment_id)
        self.experiment = experiment
        context['experiment_details'] = {
            'experiment': experiment,
            'plans': get_sample_plan_descriptions(experiment.id)
        }
        site_visit_count = SiteVisit.objects.filter(site_id=self.object.id).count()
        if site_visit_count < 1:
            site_visit_count = 1
        context['json_context'] = get_json_context(get_formsets_display_control_config(
                    self.formset_total, site_visit_count))
        context['form_action_url'] = reverse(
            'samples:site-update', kwargs={'site_id': self.kwargs['site_id']})
        self.experiment = experiment
        if self.request.POST:
            context['formsets'] = self.form_set(self.request.POST, instance=self.object)
        else:
            context['formsets'] = self.form_set(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formsets = context['formsets']
        self.object = form.save()
        if formsets.is_valid():
            formsets.instance = self.object
            instances = formsets.save(commit=False)
            for i in instances:
                i.created_by_user_id = self.request.user.id
                i.save()
            formsets.save()
        else:
            print('ERRORS_formsets: ' + str(formsets.errors))
        return super(SiteUpdateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('samples:experiment', kwargs={'experiment_id': self.experiment.id})


class SampleView(PermissionRequiredMixin, FormView):

    permission_required = IS_RESEARCH

    form_class = NewSpecimenImageForm
    template_name = 'samples/sample_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sample = get_object_or_404(Sample, id=self.kwargs['sample_id'])

        specimen_datatables_url = api_reverse(
            'samples:specimen-data-list', request=self.request, kwargs=self.kwargs)
        img_thumbnail = None
        if sample.image_thumbnail:
            img_thumbnail = {
                'path': sample.image_thumbnail.url,
                'height': sample.image_thumbnail.height,
                'width': sample.image_thumbnail.width
            }
        elif sample.image:
            img_thumbnail = {
                'path': sample.image.url,
                'height': calc_image_height(constants.SAMPLE_IMAGE_THUMBSIZE, sample.image.height, sample.image.width),
                'width': constants.SAMPLE_IMAGE_THUMBSIZE
            }
        context.update({
            'sample_info': {
                'sample_id': sample.id,
                'experiment_id': sample.site_visit.site.experiment_id,
                'uuid': sample.uuid,
                'site': sample.site_visit.site.site_name,
                'country': sample.site_visit.site.country,
                'state': sample.site_visit.site.state_region,
                'county': sample.site_visit.site.county_region,
                'visit_date': sample.site_visit.visit_date,
                'sample_type': constants.SAMPLE_TYPE_CHOICES_DICT[sample.sample_type],
                'name_no': sample.name_no,
                'entered_by': sample.created_by_user,
                'notes': sample.notes,
                'completed': sample.completed,
                'img_thumbnail': img_thumbnail
            },
            'review_permission': self.request.user.has_perm(REVIEW_SPECIMEN_PAGE),
            'container_row_header': get_datatables_container(
                get_datatables_row([
                    'Image',
                    'Partial<br/>Count',
                    'Classification',
                    'Probability<br/>(Model)',
                    '<a href="{0}" class="btn btn-sm btn-outline-danger" role="button">Classify All</a>'.format(
                        reverse('taxonomy:classify-sample', kwargs={'id': sample.id}))
                ])),
            'json_context': get_json_context(
                {'specimen_datatables_url': specimen_datatables_url}),
            'form_action_url': reverse(
                'samples:sample', kwargs={'sample_id': sample.id})
        })
        return context

    def form_valid(self, form):
        files = form.cleaned_data['image']
        sample = get_object_or_404(Sample, id=self.kwargs['sample_id'])
        created_images = 0
        try:
            for f in files:
                specimen = Specimen.objects.create(sample=sample)
                SpecimenImage.objects.create(
                    specimen=specimen,
                    image=f
                )
                created_images += 1
        except Exception:
            messages.add_message(
                self.request,
                messages.ERROR,
                'Error: An unsupported file may have been selected, please use .jpg or .png')
            created_images = 0
        messages.success(self.request, 'Succesfully added {0} new specimens'.format(created_images))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('samples:sample', kwargs={'sample_id': self.kwargs['sample_id']})


class SampleUpdateView(PermissionRequiredMixin, UpdateView):

    permission_required = IS_RESEARCH

    form_class = SampleForm
    template_name = 'samples/sample_form.html'
    action = 'update'

    def get_object(self, queryset=None):
        return get_object_or_404(Sample, id=self.kwargs['sample_id'])

    def get_context_data(self, **kwargs):
        context = super(SampleUpdateView, self).get_context_data(**kwargs)
        context['form_action_url'] = reverse('samples:sample-update', kwargs={'sample_id': self.kwargs['sample_id']})
        return context

    def get_success_url(self):
        return reverse('samples:sample', kwargs={'sample_id':  self.kwargs['sample_id']})


def specimen_view_context(specimen):
    context = {
        'specimen': specimen,
        'selected_classification':
            specimen.ai_classification if not specimen.classification
            else specimen.classification,
        'verified_classification': '' if specimen.acceptance == 0 else specimen.classification,
        'ai_classification': specimen.ai_classification,
        'probability': get_probability(specimen)
    }
    s_images = SpecimenImage.objects.filter(specimen=specimen)
    if s_images:
        image_set_large = [
            {'path': i.image_thumbnail_large.url, 'id': i.id} for i in s_images if i.image_thumbnail_large
        ]
        if not image_set_large:
            image_set_large = [{
                'path': s_images[0].image.url,
            }]
        image_set_small = [
            {
                'path': i.image_thumbnail_medium.url,
                'width': i.image_thumbnail_medium.width * 0.5,
                'height': i.image_thumbnail_medium.height * 0.5,
                'id': i.id
            } for i in s_images if i.image_thumbnail_medium if i.id != image_set_large[0]['id']
        ]

        context.update({
            'image_set_small': image_set_small,
            'image_set_large': image_set_large,
        })
    return context


class SpecimenView(PermissionRequiredMixin, FormView):

    permission_required = IS_RESEARCH

    form_class = SpecimenViewForm
    template_name = 'samples/specimen_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        specimen = get_object_or_404(Specimen, id=self.kwargs['id'])
        context.update(specimen_view_context(specimen))
        context.update({
            'form_action_url': reverse('samples:specimen', kwargs={'id': specimen.id}),
            'acceptance_choices': constants.ACCEPTANCE_CHOICES,
            'acceptance': '' if specimen.acceptance is None else constants.ACCEPTANCE_LOOKUP[specimen.acceptance]
        })
        return context

    def form_valid(self, form):
        files = form.cleaned_data['image_files']
        primary_pick = form.cleaned_data['primary_picker']
        delete_pick = form.cleaned_data['delete_picker']
        determin_pick = form.cleaned_data['determin_picker']
        if files:
            specimen = get_object_or_404(Specimen, id=self.kwargs['id'])
            created_images = 0
            try:
                for f in files:
                    SpecimenImage.objects.create(
                        specimen=specimen,
                        image=f
                    )
                    created_images += 1
            except Exception:
                messages.add_message(
                    self.request,
                    messages.ERROR,
                    'Error: An unsupported file may have been selected, please use .jpg or .png')
                created_images = 0
            messages.success(self.request, 'Succesfully added {0} new specimen images'.format(created_images))
        elif primary_pick:
            image = get_object_or_404(SpecimenImage, id=primary_pick)
            image.primary_image = True
            image.save()
            messages.success(self.request, 'Succesfully set primary image')
        elif delete_pick:
            SpecimenImage.objects.filter(id=delete_pick).delete()
            messages.success(self.request, 'Succesfully deleted image')
        elif determin_pick is not None:
            specimen = get_object_or_404(Specimen, id=self.kwargs['id'])
            specimen.acceptance = determin_pick
            if specimen.acceptance == constants.ACCEPTANCE_CONFIRMED \
                    and specimen.classification != specimen.ai_classification:
                specimen.classification = specimen.ai_classification
            elif specimen.acceptance == constants.ACCEPTANCE_REJECTED \
                    and specimen.classification == specimen.ai_classification:
                specimen.classification = None
            specimen.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('samples:specimen', kwargs={'id':  self.kwargs['id']})


class SpecimenCreateView(PermissionRequiredMixin, CreateView):

    permission_required = IS_RESEARCH

    form_class = SpecimenForm
    template_name = 'samples/specimen_create.html'
    action = 'create'

    def get_context_data(self, **kwargs):
        context = super(SpecimenCreateView, self).get_context_data(**kwargs)
        sample = get_object_or_404(Sample, id=self.kwargs['sample_id'])
        context.update({
            'form_action_url': reverse('samples:specimen-create', kwargs={'sample_id': sample.id}),
        })
        context.update({
            'json_context': get_json_context({
                'datatables_url': api_reverse('taxonomy:morphospecies-picker-list',
                                              request=self.request, kwargs=kwargs),
                'first_picker_choices': GBIF_RANK_CHOICES_WO_BLANK_LIST,
                'first_picker_text': 'any rank',
                'ACCEPTANCE_VALUE_LOOKUP': constants.ACCEPTANCE_VALUE_LOOKUP,
                'ai_classification_id': None
            }),
            'container_row_header': get_datatables_container(
                get_datatables_row([
                    'Name',
                    'Canonical Name',
                ])),
            'sample': sample
        })
        return context

    def form_valid(self, form):
        sample = get_object_or_404(Sample, id=self.kwargs['sample_id'])
        form.instance.sample_id = sample.id
        form.instance.created_by_user_id = self.request.user.id
        return super(SpecimenCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('samples:specimen', kwargs={'id': self.object.id})


class SpecimenUpdateView(PermissionRequiredMixin, UpdateView):

    permission_required = IS_RESEARCH

    form_class = SpecimenForm
    template_name = 'samples/specimen_update.html'
    action = 'update'

    def get_object(self, queryset=None):
        return get_object_or_404(Specimen, id=self.kwargs['id'])

    def get_context_data(self, **kwargs):
        context = super(SpecimenUpdateView, self).get_context_data(**kwargs)
        context.update(specimen_view_context(self.object))
        context.update({
            'form_action_url': reverse('samples:specimen-update', kwargs={'id': self.kwargs['id']}),
        })
        context.update({
            'json_context': get_json_context({
                'datatables_url': api_reverse('taxonomy:morphospecies-picker-list',
                                              request=self.request, kwargs=kwargs),
                'first_picker_choices': GBIF_RANK_CHOICES_WO_BLANK_LIST,
                'first_picker_text': 'any rank',
                'ACCEPTANCE_VALUE_LOOKUP': constants.ACCEPTANCE_VALUE_LOOKUP,
                'ai_classification_id': self.object.ai_classification.id if self.object.ai_classification else None
            }),
            'container_row_header': get_datatables_container(
                get_datatables_row([
                    'Name',
                    'Canonical Name',
                ]))})
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        if context['object'].ai_classification and form.instance.classification:
            if context['object'].ai_classification != \
                form.instance.classification and form.instance.acceptance != \
                    constants.ACCEPTANCE_REJECTED:
                form.instance.acceptance = constants.ACCEPTANCE_REJECTED
            elif context['object'].ai_classification == \
                form.instance.classification and form.instance.acceptance == \
                    constants.ACCEPTANCE_REJECTED:
                form.instance.classification = None
        elif context['object'].ai_classification and form.instance.acceptance == constants.ACCEPTANCE_CONFIRMED:
            form.instance.classification = context['object'].ai_classification
        return super(SpecimenUpdateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('samples:specimen', kwargs={'id': self.kwargs['id']})


class SpecimenDeleteView(PermissionRequiredMixin, DeleteView):

    permission_required = IS_RESEARCH

    model = Specimen
    template_name = 'samples/specimen_confirm_delete.html'

    def get_object(self, queryset=None):
        return get_object_or_404(Specimen, id=self.kwargs['id'])

    def get_success_url(self):
        return reverse('samples:sample', kwargs={'sample_id': self.kwargs['sample_id']})


class SpecimensView(PermissionRequiredMixin, FormView):

    permission_required = IS_RESEARCH + [REVIEW_SPECIMEN_PAGE]

    form_class = JSONFieldForm
    template_name = 'samples/specimens.html'

    _sv_confirm_ids = 'confirm_ids'
    _sv_reject_ids = 'reject_ids'
    _sv_json_data = {
        _sv_confirm_ids: [],
        _sv_reject_ids: []
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'id' not in self.kwargs:
            self.kwargs['id'] = 0
        if 'sample_id' not in self.kwargs:
            self.kwargs['sample_id'] = 0
        datatables_url = api_reverse('samples:specimen-all-data-list',
                                     request=self.request, kwargs=self.kwargs)
        Experiment.objects.values('name', 'id')
        context.update({
            'container_row_header': get_datatables_container(
                get_datatables_row([
                    'Image',
                    'View</br>Edit',
                    'Sample',
                    'Classification',
                    'AI Classification<br/>(model)',
                    'AI Review'
                ])),
            'json_context': get_json_context({
                'datatables_url': datatables_url,
                'first_picker_choices': constants.ACCEPTANCE_CHOICES,
                'first_picker_text': 'AI ID Acceptance',
                'json_data': self._sv_json_data,
            }),
            'acceptance_picker_choices': constants.ACCEPTANCE_CHOICES,
            'form_action_url': reverse(
                'samples:specimens-experiment-sample',
                kwargs={'id': self.kwargs['id'],
                        'sample_id': self.kwargs['sample_id']})
        })
        return context

    def form_invalid(self, form):
        messages.error(self.request, 'Form Error, changes not saved')
        return super().form_invalid(form)

    def form_valid(self, form):
        confirm_ids = form.cleaned_data['json_data'][self._sv_confirm_ids]
        reject_ids = form.cleaned_data['json_data'][self._sv_reject_ids]
        confirmed_ids = [int(v) for v in confirm_ids] if confirm_ids else []
        rejected_ids = [int(v) for v in reject_ids] if reject_ids else []
        confirm_count = 0
        for i in confirmed_ids:
            specimen = get_object_or_404(Specimen, id=i)
            specimen.acceptance = constants.ACCEPTANCE_CONFIRMED
            specimen.classification = specimen.ai_classification
            specimen.save()
            confirm_count += 1
        Specimen.objects.filter(
            id__in=rejected_ids, acceptance=constants.ACCEPTANCE_PENDING).update(
                acceptance=constants.ACCEPTANCE_REJECTED)
        messages.success(
            self.request, 'Succesfully confirmed {0} specimens and rejected {1}'.format(
                confirm_count, len(rejected_ids)))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'samples:specimens-experiment-sample',
            kwargs={
                'id': self.kwargs['id'],
                'sample_id': self.kwargs['sample_id']
            }
        )


@permission_required(IS_RESEARCH)
def experiment_ai_csv(request, id):
    # get query params and sanitize
    experiment = get_object_or_404(Experiment, id=id)
    sample_types = request.GET.getlist('sampleTypes')
    sample_types = [v for v in sample_types if v in constants.SAMPLE_TYPE_CHOICES_ALL]
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
    sample_types = [v for v in sample_types if v in constants.SAMPLE_TYPE_CHOICES_ALL]
    sites = request.GET.getlist('sites2')
    if not all([v.isnumeric() for v in sites]):
        return HttpResponse(status=404)
    sites = [int(v) for v in sites]
    other_experiments = request.GET.getlist('otherExperiments2')
    if not all([v.isnumeric() for v in other_experiments]):
        return HttpResponse(status=404)
    other_experiments = [int(v) for v in other_experiments]
    all_exp = other_experiments + [experiment.id]
    headers_arr = constants.EXP_HEADERS_ARR + indices
    morpho_headers = [dict.fromkeys(headers_arr, '') for _ in range(3)]
    unknown_species = 'Undetermined specimen'
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
            if not specimens.count() and not sample.completed:
                # indicates a planned sample that was not actually taken or completed
                continue
            n = 0
            row = {
                constants.EXP_HEAD_ARR_EXPERIMENT: this_experiment.name,
                constants.EXP_HEAD_ARR_SITE: sample.site_visit.site.site_name,
                constants.EXP_HEAD_ARR_DATE: sample.site_visit.visit_date.strftime('%d %b %Y'),
                constants.EXP_HEAD_ARR_SAMPLE_TYPE: sample.sample_type,
                constants.EXP_HEAD_ARR_SAMPLE_NAME: sample.name_no,
                unknown_species: 0  # starting count
            }
            for specimen in specimens.all():
                morphospecies_id = None
                if specimen.classification_id:
                    morphospecies_id = specimen.classification_id
                elif specimen.ai_classification_id and specimen.acceptance != constants.ACCEPTANCE_REJECTED:
                    morphospecies_id = specimen.ai_classification_id
                if export_type == constants.EXP_CSV_TYPE_REVIEWED \
                        and specimen.acceptance == constants.ACCEPTANCE_PENDING:
                    # But what about entered specimens, not ran through AI, such as counts without image?
                    # Use an entry in determined_by? But then what about deleted users?
                    morphospecies_id = None
                if morphospecies_id:
                    morpho = Morphospecies.objects.get(pk=morphospecies_id)
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
