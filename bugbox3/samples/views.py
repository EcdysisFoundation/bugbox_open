import os.path

from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db import transaction
from django.forms import inlineformset_factory
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, DeleteView, FormView, UpdateView
from rest_framework.reverse import reverse as api_reverse

from ..core import constants as constants_core
from ..core.permissions import IS_RESEARCH, REVIEW_SPECIMEN_PAGE
from ..libs.ui_helpers import (
    calc_image_height,
    get_datatables_container,
    get_datatables_row,
    get_formsets_display_control_config,
    get_probability,
)
from ..libs.utilities import get_json_context
from ..taxonomy import constants as taxa_const
from ..taxonomy.models import Morphospecies
from . import constants
from .forms import (
    ExperimentForm,
    JSONFieldForm,
    NewSpecimenImageForm,
    SampleForm,
    SamplePlanForm,
    SiteForm,
    SiteVisitForm,
    SpecimenForm,
    SpecimensWithoutImagesForm,
    SpecimenViewForm,
)
from .models import Experiment, Sample, SamplePlan, Site, SiteVisit, Specimen, SpecimenImage
from .models_query import get_sample_plan_descriptions, get_user_choices
from .timeline_events import audit_specimen_update, audit_specimen_view, audit_upload_images, timeline_events


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
            'skip_morphospecies': ', '.join(
                [v[taxa_const.FIELD_MORPHO_NAME] for v in taxa_const.SKIP_MORPHOSPECIES]),
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
        context.update({
            'action': self.action,
            'experiment_details': {
                'experiment': experiment,
                'plans': get_sample_plan_descriptions(experiment.id)
            },
            'json_context': get_json_context(get_formsets_display_control_config(
                    self.formset_total, experiment.date_per_site)),
            'form_action_url': reverse(
                'samples:site-create', kwargs={'experiment_id': self.kwargs['experiment_id']})
        })
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
        context.update({
            'site_id': self.kwargs['site_id'],
            'action': self.action,
            'experiment_details': {
                'experiment': experiment,
                'plans': get_sample_plan_descriptions(experiment.id)
            },
            'has_related_data': [
                i.visit_date for i in SiteVisit.objects.filter(site_id=self.object.id) if i.has_related_data
            ]
        })
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


class SiteDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = IS_RESEARCH

    model = Site
    template_name = 'samples/confirm_delete.html'

    def get_object(self, queryset=None):
        return get_object_or_404(Site, id=self.kwargs['id'])

    def get_success_url(self):
        return reverse('samples:experiment', kwargs={'experiment_id': self.kwargs['experiment_id']})


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
            if os.path.isfile(sample.image_thumbnail.path):
                img_thumbnail = {
                    'path': sample.image_thumbnail.url,
                    'height': sample.image_thumbnail.height,
                    'width': sample.image_thumbnail.width
                }
        elif sample.image:
            if os.path.isfile(sample.image.path):
                img_thumbnail = {
                    'path': sample.image.url,
                    'height': calc_image_height(constants.SAMPLE_IMAGE_THUMBSIZE, sample.image.height, sample.image.width),
                    'width': constants.SAMPLE_IMAGE_THUMBSIZE
                }
        sample_type = constants.SAMPLE_TYPE_CHOICES_DICT[sample.sample_type] \
            if sample.sample_type in constants.SAMPLE_TYPE_CHOICES_DICT.keys() \
            else sample.sample_type
        context.update({
            'sample_info': {
                'sample_id': sample.id,
                'experiment_id': sample.site_visit.site.experiment_id,
                'uuid': sample.uuid,
                'site': sample.site_visit.site.site_name,
                'country': sample.site_visit.site.country,
                'state': sample.site_visit.site.state_region,
                'county': sample.site_visit.site.county_region,
                'visit_date': sample.site_visit.visit_date.strftime("%d-%b-%Y"),
                'sample_type': sample_type,
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
                specimen = Specimen.objects.create(
                    sample=sample,
                    created_by_user=self.request.user)
                SpecimenImage.objects.create(
                    specimen=specimen,
                    image=f,
                    uploaded_by_user=self.request.user
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
            specimen.ai_classification if not specimen.classification and
            specimen.acceptance != constants.ACCEPTANCE_REJECTED else specimen.classification,
        'verified_classification': specimen.classification,
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


class SpecimsWithoutImagesFormView(PermissionRequiredMixin, FormView):

    permission_required = IS_RESEARCH

    form_class = SpecimensWithoutImagesForm
    template_name = 'samples/specimens_wo_images.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sample = get_object_or_404(Sample, id=self.kwargs['id'])
        morpho_names = [v[taxa_const.FIELD_MORPHO_NAME] for v in taxa_const.SKIP_MORPHOSPECIES]
        existing_names = []
        for m in morpho_names:
            if Specimen.objects.filter(classification__name=m, sample_id=sample.id):
                existing_names.append(m)
        use_names = [v for v in morpho_names if v not in existing_names]
        sample_type = constants.SAMPLE_TYPE_CHOICES_DICT[sample.sample_type] \
            if sample.sample_type in constants.SAMPLE_TYPE_CHOICES_DICT.keys() \
            else sample.sample_type
        context.update({
            'morpho_names': ', '.join(morpho_names),
            'existing_names': ', '.join(existing_names),
            'use_names': use_names,
            'sample_link': reverse(
                'samples:sample', kwargs={'sample_id': self.kwargs['id']}),
            'experiment': sample.site_visit.site.experiment.name,
            'experiment_id': sample.site_visit.site.experiment.id,
            'site_name': sample.site_visit.site.site_name,
            'visit_date': sample.site_visit.visit_date.strftime("%d-%b-%Y"),
            'sample_type': sample_type,
            'name_no': sample.name_no,
            'form_action_url': reverse(
                'samples:specimens-wo-img', kwargs={'id': self.kwargs['id']})
        })
        return context

    def form_valid(self, form):
        sample = get_object_or_404(Sample, id=self.kwargs['id'])
        entered_names = []
        for v in taxa_const.SKIP_MORPHOSPECIES:
            name = v[taxa_const.FIELD_MORPHO_NAME]
            if name in form.cleaned_data:
                if form.cleaned_data[name]:
                    morhpospecies = get_object_or_404(Morphospecies, name=name)
                    Specimen.objects.create(
                        sample=sample,
                        classification=morhpospecies,
                        created_by_user=self.request.user,
                        partial_count=form.cleaned_data[name]
                    )
                    entered_names.append(name)
        messages.success(
            self.request, 'Succesfully entered counts for {0}'.format(
                ', '.join(entered_names)
            ))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('samples:sample', kwargs={'sample_id':  self.kwargs['id']})


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
            'acceptance': '' if specimen.acceptance is None else constants.ACCEPTANCE_LOOKUP[specimen.acceptance],
            'json_context': get_json_context({
                'timeline_events': timeline_events(specimen)
            })
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
                        image=f,
                        uploaded_by_user=self.request.user
                    )
                    created_images += 1
                audit_upload_images(self.request.user, specimen, created_images)
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
            initial = {constants.FIELD_SPECIMEN_ACCEPTANCE: specimen.acceptance}
            specimen.acceptance = determin_pick
            if specimen.acceptance == constants.ACCEPTANCE_CONFIRMED \
                    and specimen.classification != specimen.ai_classification:
                specimen.classification = specimen.ai_classification
                specimen.reviewer_user = self.request.user
            elif specimen.acceptance == constants.ACCEPTANCE_REJECTED \
                    and specimen.classification == specimen.ai_classification:
                specimen.classification = None
                specimen.reviewer_user = None
            specimen.save()
            audit_specimen_view(initial, self.request.user, specimen)
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
                'first_picker_choices': taxa_const.GBIF_RANK_CHOICES_WO_BLANK_LIST,
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
                'first_picker_choices': taxa_const.GBIF_RANK_CHOICES_WO_BLANK_LIST,
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
        if form.initial[constants.FIELD_SPECIMEN_CLASSIFICATION] != form.instance.classification:
            context['object'].reviewer_user = self.request.user
        audit_specimen_update(form, self.request.user, context['object'])
        return super(SpecimenUpdateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('samples:specimen', kwargs={'id': self.kwargs['id']})


class SpecimenDeleteView(PermissionRequiredMixin, DeleteView):

    permission_required = IS_RESEARCH

    model = Specimen
    template_name = 'samples/confirm_delete.html'

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
    _sv_new_classifications = 'new_classifications'
    _sv_json_data = {
        _sv_confirm_ids: [],  # specimen ids
        _sv_reject_ids: [],  # specimen ids
        _sv_new_classifications: {},  # key:value pairs of specimen_id: morphospecies_id
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        experiment_name = None
        sample_name = None
        if 'id' not in self.kwargs:
            self.kwargs['id'] = 0
        if self.kwargs['id']:
            experiment_name = get_object_or_404(Experiment, id=self.kwargs['id']).name
        if 'sample_id' not in self.kwargs:
            self.kwargs['sample_id'] = 0
        if self.kwargs['sample_id']:
            sample_name = get_object_or_404(Sample, id=self.kwargs['sample_id']).name_no
        datatables_url = api_reverse('samples:specimen-all-data-list',
                                     request=self.request, kwargs=self.kwargs)
        context.update({
            'container_row_header_2': get_datatables_container(
                get_datatables_row([
                    'Name',
                    'Canonical Name',
                ])),
            'container_row_header': get_datatables_container(
                get_datatables_row([
                    'Image',
                    'Archival',
                    'Sample',
                    'Classification',
                    'AI Classification<br/>(model)',
                    'AI Review'
                ])),
            'json_context': get_json_context({
                'datatables_url': datatables_url,
                'json_data': self._sv_json_data,
                'datatables_url_2': api_reverse('taxonomy:morphospecies-picker-list',
                                                request=self.request, kwargs=kwargs),
                'second_picker_choices': taxa_const.GBIF_RANK_CHOICES_WO_BLANK_LIST,
                'second_picker_text': 'any rank',
                'acceptance_choices': constants.ACCEPTANCE_CHOICES,
                'user_choices': get_user_choices(),
                'state_choices_dict': constants_core.STATE_CHOICES,
                'country_choices': constants_core.COUNTRY_CHOICES,
                'tag_choices': constants.TAG_CHOICES
            }),
            'experiment_name': experiment_name,
            'sample_name': sample_name,
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
        new_classifications = form.cleaned_data['json_data'][self._sv_new_classifications]
        # do some sanitizing and cast any string ids.
        if isinstance(self._sv_json_data[self._sv_new_classifications], dict):
            new_classifications = {int(key): int(v) for key, v in new_classifications.items()}
        else:
            new_classifications = self._sv_json_data[self._sv_new_classifications]
        confirmed_ids = [int(v) for v in confirm_ids] if confirm_ids else []
        rejected_ids = [int(v) for v in reject_ids] if reject_ids else []
        add_confirm_count = 0
        add_reject_count = 0
        for specimen_id, morhpo_id in new_classifications.items():
            specimen = get_object_or_404(Specimen, id=specimen_id)
            ai_classification_id = specimen.ai_classification.id if specimen.ai_classification else None
            if ai_classification_id == morhpo_id:
                specimen.acceptance = constants.ACCEPTANCE_CONFIRMED
                specimen.classification = specimen.ai_classification
                specimen.reviewer_user = self.request.user
                specimen.save()
                add_confirm_count += 1
            else:
                morpho = get_object_or_404(Morphospecies, id=morhpo_id)
                specimen.classification = morpho
                specimen.acceptance = constants.ACCEPTANCE_REJECTED
                specimen.reviewer_user = self.request.user
                specimen.save()
                add_reject_count += 1
            # prioritize new_classifications for confirmed or rejected.
            if specimen_id in confirmed_ids:
                confirmed_ids.remove(specimen_id)
            if specimen_id in rejected_ids:
                rejected_ids.remove(specimen_id)
        for i in confirmed_ids:
            specimen = get_object_or_404(Specimen, id=i)
            specimen.acceptance = constants.ACCEPTANCE_CONFIRMED
            specimen.classification = specimen.ai_classification
            specimen.reviewer_user = self.request.user
            specimen.save()
        Specimen.objects.filter(
            id__in=rejected_ids, acceptance=constants.ACCEPTANCE_PENDING).update(
                acceptance=constants.ACCEPTANCE_REJECTED)
        messages.success(
            self.request, 'Succesfully confirmed {0} AI classifications and rejected {1}'.format(
                len(confirmed_ids) + add_confirm_count,
                len(rejected_ids) + add_reject_count))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'samples:specimens-experiment-sample',
            kwargs={
                'id': self.kwargs['id'],
                'sample_id': self.kwargs['sample_id']
            }
        )
