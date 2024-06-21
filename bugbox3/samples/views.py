from django.contrib import messages
from django.db import transaction
from django.forms import inlineformset_factory
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, FormView, UpdateView
from rest_framework.reverse import reverse as api_reverse
from rest_framework.viewsets import ReadOnlyModelViewSet

from ..core.views import DatatablesModelViewSetMixin
from ..libs.ui_helpers import (
    calc_image_height,
    get_datatables_container,
    get_datatables_row,
    get_formsets_display_control_config,
    get_probability,
)
from ..libs.utilities import get_json_context
from ..taxonomy.constants import GBIF_RANK_SPECIES
from . import constants
from .forms import (
    ExperimentForm,
    NewSpecimenImageForm,
    SampleForm,
    SamplePlanForm,
    SiteForm,
    SiteVisitForm,
    SpecimenViewForm,
)
from .models import Experiment, Sample, SamplePlan, Site, SiteVisit, Specimen, SpecimenImage
from .models_query import get_sample_plan_descriptions
from .serializers import (
    ExperimentsDatatablesSerializer,
    SamplesDatatablesSerializer,
    SitesDatatablesSerializer,
    SpecimenDatatablesSerializer,
)


class ExperimentsDatatablesViewSet(DatatablesModelViewSetMixin, ReadOnlyModelViewSet):

    serializer_class = ExperimentsDatatablesSerializer
    queryset = Experiment.objects.all().order_by(constants.FIELD_NAME)
    search_vector = [constants.FIELD_NAME, constants.FIELD_ABBREVIATION]


class SamplesDatatablesViewSet(DatatablesModelViewSetMixin, ReadOnlyModelViewSet):

    serializer_class = SamplesDatatablesSerializer
    search_vector = [constants.FIELD_SAMPLE_TYPE]

    def get_queryset(self):
        experiment_id = int(self.kwargs['experiment_id'])
        return Sample.objects.filter(site_visit__site__experiment_id=experiment_id)


class SitesDatatablesViewSet(DatatablesModelViewSetMixin, ReadOnlyModelViewSet):

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


class SpecimenDatatablesViewSet(DatatablesModelViewSetMixin, ReadOnlyModelViewSet):

    serializer_class = SpecimenDatatablesSerializer
    search_vector = [constants.FIELD_SPECIMEN_PARTIAL_COUNT]

    def get_queryset(self):
        sample_id = int(self.kwargs['sample_id'])
        return Specimen.objects.filter(sample_id=sample_id).order_by('-id')


class ExperimentsView(TemplateView):
    template_name = 'samples/experiments.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        experiments_datatables_url = api_reverse('samples:experiment-data-list',
                                                 request=self.request, kwargs=kwargs)
        context.update({'json_context': get_json_context({
            'experiments_datatables_url': experiments_datatables_url}),
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


class ExperimentView(TemplateView):
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
        context.update({
            'experiment': experiment,
            'years': years,
            'sample_plan_descriptions': description,
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


class SpecimensView(TemplateView):
    template_name = 'samples/specimens.html'


class ExperimentSamplePlanCreateView(CreateView):

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


class ExperimentSamplePlanUpdateView(UpdateView):

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


class SiteCreateView(CreateView):

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
        with transaction.atomic():
            self.object = form.save()
            if formsets.is_valid():
                formsets.instance = self.object
                formsets.save()
            else:
                print('ERRORS_formsets: ' + str(formsets.errors))
        return super(SiteCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('samples:experiment', kwargs={'experiment_id': self.kwargs['experiment_id']})


class SiteUpdateView(UpdateView):
    form_class = SiteForm
    template_name = 'samples/site_form.html'
    action = 'update'

    formset_total = 10

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
        with transaction.atomic():
            self.object = form.save()
            if formsets.is_valid():
                formsets.instance = self.object
                formsets.save()
            else:
                print('ERRORS_formsets: ' + str(formsets.errors))
        return super(SiteUpdateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('samples:experiment', kwargs={'experiment_id': self.experiment.id})


class SampleView(FormView):
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
                'entered_by': 'P. Laceholder',
                'notes': sample.notes,
                'completed': sample.completed,
                'img_thumbnail': img_thumbnail
            },
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


class SampleUpdateView(UpdateView):
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


class SpecimenView(FormView):
    form_class = SpecimenViewForm
    template_name = 'samples/specimen_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        specimen = get_object_or_404(Specimen, id=self.kwargs['id'])
        s_images = SpecimenImage.objects.filter(
            specimen=specimen)
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
        context.update({
            'specimen': specimen,
            'classification':
                specimen.ai_classification if specimen.ai_classification and specimen.acceptance == 0
                else specimen.classification,
            'rank_species': GBIF_RANK_SPECIES,
            'probability': get_probability(specimen),
            'form_action_url': reverse('samples:specimen', kwargs={'id': specimen.id})
        })
        return context

    def form_valid(self, form):
        files = form.cleaned_data['image_files']
        primary_pick = form.cleaned_data['primary_picker']
        delete_pick = form.cleaned_data['delete_picker']
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
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('samples:specimen', kwargs={'id':  self.kwargs['id']})
