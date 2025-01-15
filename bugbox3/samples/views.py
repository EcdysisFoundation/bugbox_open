import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.db import transaction
from django.db.models.fields import BLANK_CHOICE_DASH
from django.forms import inlineformset_factory
from django.http import Http404, JsonResponse
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.views.generic import TemplateView
from django.views.generic.edit import (CreateView, DeleteView, FormView,
                                       UpdateView)
from organizations.models import OrganizationUser
from rest_framework.reverse import reverse as api_reverse

from ..core import constants as constants_core
from ..core.models import LookupChoices
from ..core.permissions import IS_RESEARCH, REVIEW_SPECIMEN_PAGE
from ..libs.ui_helpers import (calc_image_height, get_datatables_container,
                               get_datatables_row,
                               get_formsets_display_control_config,
                               get_probability)
from ..libs.utilities import crop_img_to_grid, get_json_context, get_media_url
from ..taxonomy import constants as taxa_const
from ..taxonomy.models import Morphospecies
from . import constants
from .forms import (ExperimentForm, JSONFieldSpecimensForm, MultiSpecimenForm,
                    SampleDetailForm, SampleForm, SamplePlanForm, SiteForm,
                    SiteVisitForm, SpecimenForm, SpecimenImageForm,
                    SpecimensWithoutImagesForm, SpecimenViewForm)
from .models import (Experiment, MultiSpecimenImage, Sample, SamplePlan, Site,
                     SiteVisit, Specimen, SpecimenImage)
from .models_query import get_sample_plan_descriptions, get_user_choices
from .timeline_events import (audit_specimen_update, audit_specimen_view,
                              audit_upload_images, timeline_events)


class ExperimentsView(PermissionRequiredMixin, TemplateView):

    permission_required = IS_RESEARCH

    template_name = 'samples/experiments.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        experiments_datatables_url = api_reverse('samples:experiment-data-list',
                                                 request=self.request, kwargs=kwargs)
        orgs = OrganizationUser.objects.filter(
            user=self.request.user).values(
                'organization_id', 'organization__name').order_by('organization_id')
        org_choices = [(o['organization_id'], o['organization__name']) for o in orgs]
        context.update({
            'json_context': get_json_context({
                'experiments_datatables_url': experiments_datatables_url,
                'org_choices': org_choices
            }),
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
        try:
            experiment = Experiment.objects.user_access(
                self.request.user).get(id=kwargs['experiment_id'])
        except Experiment.DoesNotExist:
            raise Http404

        if experiment.from_year == experiment.to_year:
            years = str(experiment.from_year)
        else:
            years = str(experiment.from_year) + ' - ' + str(experiment.to_year)
        description = [v['description'] for v in get_sample_plan_descriptions(
            experiment.id)]
        sites_datatables_url = api_reverse(
            'samples:site-data-list', request=self.request, kwargs=kwargs)
        experiment_sites = Site.objects.user_access(self.request.user).filter(
            experiment_id=experiment.id).order_by(
                constants.FIELD_SITE_SITE_NAME)
        other_experiments = Experiment.objects.user_access(self.request.user).exclude(
            id=experiment.id).order_by(constants.FIELD_ABBREVIATION)
        context.update({
            'experiment': experiment,
            'experiment_sites': experiment_sites,
            'other_experiments': other_experiments,
            'sample_types': LookupChoices.objects.get_field_choices_w_blank(
                experiment.organization_id, constants.FIELD_SAMPLE_TYPE),
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

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        org_choices = []
        orgs = OrganizationUser.objects.filter(
            user=self.request.user).values(
                'organization_id', 'organization__name').order_by('organization_id')
        if len(orgs) > 1:
            org_choices += [BLANK_CHOICE_DASH[0]]
        org_choices += [(o['organization_id'], o['organization__name']) for o in orgs]
        form.fields['organization'].choices = org_choices
        return form

    def get_context_data(self, **kwargs):
        context = super(ExperimentSamplePlanCreateView, self).get_context_data(**kwargs)
        context['json_context'] = get_json_context(get_formsets_display_control_config(
                    self.formset_total, self.formset_intial))
        context['form_action_url'] = reverse('samples:experiment-sample-plan-create')
        if self.request.POST:
            context['formsets'] = self.sample_plan_form_set(self.request.POST, form_kwargs={'request': self.request})
        else:
            context['formsets'] = self.sample_plan_form_set(form_kwargs={'request': self.request})
        return context

    def form_valid(self, form):
        # check belongs to org
        orgs = list(OrganizationUser.objects.filter(
            user=self.request.user).values_list('organization', flat=True))
        org = form.cleaned_data['organization'].id
        if org not in orgs:
            raise Http404
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
        try:
            experiment = Experiment.objects.user_access(self.request.user).get(
                id=self.kwargs['experiment_id'])
        except Experiment.DoesNotExist:
            raise Http404

        return experiment

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

    def get_form_kwargs(self):
        kwargs = super(SiteCreateView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(SiteCreateView, self).get_context_data(**kwargs)
        try:
            experiment = Experiment.objects.user_access(self.request.user).get(
                id=self.kwargs['experiment_id'])
        except Experiment.DoesNotExist:
            raise Http404

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
        try:
            site = Site.objects.user_access(self.request.user).get(
                id=self.kwargs['site_id'])
        except Site.DoesNotExist:
            raise Http404
        return site

    def get_context_data(self, **kwargs):
        context = super(SiteUpdateView, self).get_context_data(**kwargs)
        try:
            experiment = Experiment.objects.user_access(self.request.user).get(
                id=self.object.experiment_id)
        except Experiment.DoesNotExist:
            raise Http404
        self.experiment = experiment
        context.update({
            'site_id': self.kwargs['site_id'],
            'action': self.action,
            'experiment_details': {
                'experiment': experiment,
                'plans': get_sample_plan_descriptions(
                    self.request.user, experiment.id)
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
        try:
            site = Site.objects.user_access(self.request.user).get(
                id=self.kwargs['id']
            )
        except Site.DoesNotExist:
            raise Http404

        return site

    def get_success_url(self):
        return reverse('samples:experiment', kwargs={'experiment_id': self.kwargs['experiment_id']})


class SampleView(PermissionRequiredMixin, FormView):

    permission_required = IS_RESEARCH

    form_class = SampleDetailForm
    template_name = 'samples/sample_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            sample = Sample.objects.user_access(self.request.user).get(id=self.kwargs['sample_id'])
        except Sample.DoesNotExist:
            raise Http404

        specimen_datatables_url = api_reverse(
            'samples:specimen-data-list', request=self.request, kwargs=self.kwargs)
        samples_datatables_url = api_reverse(
            'samples:sample-data-list',
            request=self.request,
            kwargs={'experiment_id': sample.site_visit.site.experiment_id}
        )
        experiment_choices = [(
            api_reverse('samples:sample-data-list', request=self.request, kwargs={'experiment_id': i['id']}),
            i['name']) for i in Experiment.objects.user_access(
                self.request.user).order_by(constants.FIELD_NAME).values('id', constants.FIELD_NAME)]
        img_thumbnail = None
        if sample.image_thumbnail:
            if default_storage.exists(sample.image_thumbnail.name):
                img_thumbnail = {
                    'path': get_media_url(sample.image_thumbnail),
                    'height': sample.image_thumbnail.height,
                    'width': sample.image_thumbnail.width
                }
        elif sample.image:
            if default_storage.exists(sample.image.name):
                img_thumbnail = {
                    'path': get_media_url(sample.image),
                    'height': calc_image_height(
                        constants.SAMPLE_IMAGE_THUMBSIZE, sample.image.height, sample.image.width),
                    'width': constants.SAMPLE_IMAGE_THUMBSIZE
                }
        sample_type = LookupChoices.objects.get_field_dict_w_blank(
            sample.site_visit.site.experiment.organization_id, constants.FIELD_SAMPLE_TYPE)[sample.sample_type] \
            if sample.sample_type in LookupChoices.objects.get_field_dict_w_blank(
            sample.site_visit.site.experiment.organization_id, constants.FIELD_SAMPLE_TYPE).keys() \
            else sample.sample_type
        has_data = sample.completed
        if not has_data:
            if Specimen.objects.filter(sample_id=sample.id).first():
                has_data = True
        d_none = 'd-none' if not settings.AI_INFERENCE_URL else ''
        classify_btn = '<a href="{0}"'.format(
            reverse('taxonomy:classify-sample', kwargs={'id': sample.id})) + \
            ' class="btn btn-sm btn-outline-danger{0}"'.format(d_none) + \
            ' role="button" id="classify-all">Classify All</a>'
        context.update({
            'sample_info': {
                'sample_id': sample.id,
                'experiment_name': sample.site_visit.site.experiment.name,
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
                'img_thumbnail': img_thumbnail,
                'has_data': has_data
            },
            'review_permission': self.request.user.has_perm(REVIEW_SPECIMEN_PAGE),
            'container_row_header': get_datatables_container(
                get_datatables_row([
                    'Image',
                    'Partial<br/>Count',
                    'Classification',
                    'Probability<br/>(Model)',
                    classify_btn
                ])),
            'sample_container_row_header': get_datatables_container(
                get_datatables_row([
                    'Site',
                    'Date',
                    'Type',
                    'Name',
                ])),
            'json_context': get_json_context({
                'specimen_datatables_url': specimen_datatables_url,
                'samples_datatables_url': samples_datatables_url,
                'experiment_choices': experiment_choices,
                'experiment_id': sample.site_visit.site.experiment_id,
                'experiment_name': sample.site_visit.site.experiment.name,
                'image_upload_url': reverse('samples:specimen-image-upload', kwargs={'sample_id': sample.id}),
                'csrf_token': get_token(self.request)
                }),
            'form_action_url': reverse(
                'samples:sample', kwargs={'sample_id': sample.id})
        })
        return context

    def form_valid(self, form):
        json_data = form.cleaned_data['json_data']
        move_json_data = form.cleaned_data['move_json_data']
        if json_data:
            if not all([isinstance(v, int) for v in json_data['ids']]):
                raise ValidationError(mark_safe('non-integers provided in form as ids'))
            Specimen.objects.user_access(self.request.user).filter(id__in=json_data['ids']).delete()
            messages.warning(self.request, 'Succesfully deleted {0} specimens'.format(len(json_data['ids'])))
        if move_json_data:
            if move_json_data['move_ids'] and move_json_data['move_sample_id']:
                try:
                    s = Sample.objects.user_access(self.request.user).get(id=move_json_data['move_sample_id'])
                except Sample.DoesNotExist:
                    return Http404
                Specimen.objects.user_access(self.request.user).filter(
                    id__in=move_json_data['move_ids']).update(sample_id=s.id)
                messages.warning(self.request, 'Succesfully moved {0} specimens to sample ID {1}'.format(
                    len(move_json_data['move_ids']),
                    s.id
                ))
            else:
                messages.warning(self.request, 'No specimens or samples were seleceted to move.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('samples:sample', kwargs={'sample_id': self.kwargs['sample_id']})


@permission_required(IS_RESEARCH)
def specimen_image_upload(request, sample_id):
    if request.method == 'POST':
        try:
            sample = Sample.objects.user_access(request.user).get(id=sample_id)
        except Sample.DoesNotExist:
            raise Http404
        form = SpecimenImageForm(request.POST, request.FILES)

        if form.is_valid():
            data = form.cleaned_data
            specimen = Specimen.objects.create(
                        sample=sample,
                        created_by_user=request.user)
            SpecimenImage.objects.create(
                specimen=specimen,
                image=data['image'],
                uploaded_by_user=request.user
            )
            return JsonResponse({'success': 'image uploaded successfully'}, status=200)
        return JsonResponse({'error': form.errors}, status=400)
    return JsonResponse({'error': "Method Not Allowed"}, status=405)


class SampleUpdateView(PermissionRequiredMixin, UpdateView):

    permission_required = IS_RESEARCH

    form_class = SampleForm
    template_name = 'samples/sample_form.html'
    action = 'update'

    def get_object(self, queryset=None):
        try:
            return Sample.objects.user_access(self.request.user).get(id=self.kwargs['sample_id'])
        except Sample.DoesNotExist:
            raise Http404

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
            {'path': get_media_url(i.image_thumbnail_large), 'id': i.id} for i in s_images if i.image_thumbnail_large
        ]
        if not image_set_large:
            image_set_large = [{
                'path': get_media_url(s_images[0].image),
            }]
        image_set_small = [
            {
                'path': get_media_url(i.image_thumbnail_medium),
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


class SampleDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = IS_RESEARCH

    model = Sample
    template_name = 'samples/confirm_delete.html'

    def get_object(self, queryset=None):
        try:
            return Sample.objects.user_access(self.request.user).get(id=self.kwargs['id'])
        except Sample.DoesNotExist:
            raise Http404

    def get_success_url(self):
        return reverse('samples:experiment', kwargs={'experiment_id': self.kwargs['experiment_id']})


class SpecimensWithoutImagesFormView(PermissionRequiredMixin, FormView):

    permission_required = IS_RESEARCH

    form_class = SpecimensWithoutImagesForm
    template_name = 'samples/specimens_wo_images.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            sample = Sample.objects.user_access(self.request.user).get(id=self.kwargs['id'])
        except Sample.DoesNotExist:
            raise Http404
        morpho_names = [v[taxa_const.FIELD_MORPHO_NAME] for v in taxa_const.SKIP_MORPHOSPECIES]
        existing_names = []
        for m in morpho_names:
            if Specimen.objects.filter(classification__name=m, sample_id=sample.id):
                existing_names.append(m)
        use_names = [v for v in morpho_names if v not in existing_names]
        sample_type = LookupChoices.objects.get_field_dict_w_blank(
            constants.FIELD_SAMPLE_TYPE)[sample.sample_type] \
            if sample.sample_type in LookupChoices.objects.get_field_dict_w_blank(
            constants.FIELD_SAMPLE_TYPE).keys() \
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
        try:
            sample = Sample.objects.user_access(self.request.user).get(id=self.kwargs['id'])
        except Sample.DoesNotExist:
            raise Http404
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
        try:
            specimen = Specimen.objects.user_access(self.request.user).get(id=self.kwargs['id'])
        except Specimen.DoesNotExist:
            raise Http404
        context.update(specimen_view_context(specimen))
        context.update({
            'form_action_url': reverse('samples:specimen', kwargs={'id': specimen.id}),
            'review_permission': self.request.user.has_perm(REVIEW_SPECIMEN_PAGE),
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
            try:
                specimen = Specimen.objects.user_access(self.request.user).get(id=self.kwargs['id'])
            except Specimen.DoesNotExist:
                raise Http404
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
            try:
                image = SpecimenImage.objects.user_access(self.request.user).get(id=primary_pick)
            except SpecimenImage.DoesNotExist:
                raise Http404
            image.primary_image = True
            image.save()
            messages.success(self.request, 'Succesfully set primary image')
        elif delete_pick:
            SpecimenImage.objects.user_access(self.request.user).filter(id=delete_pick).delete()
            messages.success(self.request, 'Succesfully deleted image')
        elif determin_pick is not None:
            try:
                specimen = Specimen.objects.user_access(self.request.user).get(id=self.kwargs['id'])
            except Specimen.DoesNotExist:
                raise Http404
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
        try:
            sample = Sample.objects.user_access(self.request.user).get(id=self.kwargs['sample_id'])
        except Sample.DoesNotExist:
            raise Http404
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
        try:
            sample = Sample.objects.user_access(self.request.user).get(id=self.kwargs['sample_id'])
        except Sample.DoesNotExist:
            raise Http404
        if not form.instance.classification:
            messages.error(
                self.request, 'A verified classification is required, please select one to create.')
            return redirect('samples:specimen-create', sample_id=sample.id)
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
        try:
            return Specimen.objects.user_access(self.request.user).get(id=self.kwargs['id'])
        except Specimen.DoesNotExist:
            raise Http404

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['review_permission'] = self.request.user.has_perm(REVIEW_SPECIMEN_PAGE)
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(SpecimenUpdateView, self).get_context_data(**kwargs)
        context.update(specimen_view_context(self.object))
        context.update({
            'form_action_url': reverse('samples:specimen-update', kwargs={'id': self.kwargs['id']}),
            'review_permission': self.request.user.has_perm(REVIEW_SPECIMEN_PAGE),
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

    def form_invalid(self, form):
        messages.error(self.request, 'Form Error, changes not saved')
        print(form.errors)
        return super().form_invalid(form)

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
        if form.initial[constants.FIELD_SPECIMEN_CLASSIFICATION]:
            if not form.instance.classification:
                context['object'].reviewer_user = None
            elif form.initial[constants.FIELD_SPECIMEN_CLASSIFICATION] != form.instance.classification.id:
                context['object'].reviewer_user = self.request.user
        audit_specimen_update(form, self.request.user, context['object'])
        return super(SpecimenUpdateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('samples:specimen', kwargs={'id': self.kwargs['id']})


class SpecimenDeleteView(PermissionRequiredMixin, DeleteView):

    permission_required = IS_RESEARCH + [REVIEW_SPECIMEN_PAGE]

    model = Specimen
    template_name = 'samples/confirm_delete.html'

    def get_object(self, queryset=None):
        try:
            return Specimen.objects.user_access(self.request.user).get(id=self.kwargs['id'])
        except Specimen.DoesNotExist:
            raise Http404

    def get_success_url(self):
        return reverse('samples:sample', kwargs={'sample_id': self.kwargs['sample_id']})


class SpecimensView(PermissionRequiredMixin, FormView):

    permission_required = IS_RESEARCH + [REVIEW_SPECIMEN_PAGE]

    form_class = JSONFieldSpecimensForm
    template_name = 'samples/specimens.html'

    # these are also defined in sample_detail.json
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
            try:
                experiment_name = Experiment.objects.user_access(self.request.user).get(id=self.kwargs['id']).name
            except Experiment.DoesNotExist:
                raise Http404
        if 'sample_id' not in self.kwargs:
            self.kwargs['sample_id'] = 0
        if self.kwargs['sample_id']:
            try:
                sample_name = Sample.objects.user_access(self.request.user).get(id=self.kwargs['sample_id']).name_no
            except Sample.DoesNotExist:
                raise Http404
        datatables_url = api_reverse('samples:specimen-all-data-list',
                                     request=self.request, kwargs=self.kwargs)
        recent_years = sorted(
            [i for i in range(datetime.date.today().year - 10, datetime.date.today().year + 1)], reverse=True)
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
                    'AI Classification<br/>(model)'
                ])),
            'json_context': get_json_context({
                'datatables_url': datatables_url,
                'datatables_url_2': api_reverse('taxonomy:morphospecies-picker-list',
                                                request=self.request, kwargs=kwargs),
                'second_picker_choices': taxa_const.GBIF_RANK_CHOICES_WO_BLANK_LIST,
                'second_picker_text': 'any rank',
                'acceptance_choices': constants.ACCEPTANCE_CHOICES,
                'user_choices': get_user_choices(self.request.user),
                'state_choices_dict': constants_core.STATE_CHOICES,
                'country_choices': constants_core.COUNTRY_CHOICES,
                'tag_choices': LookupChoices.objects.get_field_choices(constants.FIELD_SPECIMEN_TAGS),
                'sample_type_choices': LookupChoices.objects.get_field_choices(constants.FIELD_SAMPLE_TYPE),
                'recent_year_choices': [(i, i) for i in recent_years]
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
            try:
                specimen = Specimen.objects.user_access(self.request.user).get(id=specimen_id)
            except Specimen.DoesNotExist:
                raise Http404
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
            try:
                specimen = Specimen.objects.user_access(self.request.user).get(id=i)
            except Specimen.DoesNotExist:
                raise Http404
            specimen.acceptance = constants.ACCEPTANCE_CONFIRMED
            specimen.classification = specimen.ai_classification
            specimen.reviewer_user = self.request.user
            specimen.save()
        Specimen.objects.user_access(self.request.user).filter(
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


class MultiSpecimeImageView(PermissionRequiredMixin, FormView):

    permission_required = IS_RESEARCH

    form_class = MultiSpecimenForm
    template_name = 'samples/multispecimen_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            sample = Sample.objects.user_access(self.request.user).get(id=self.kwargs['sample_id'])
        except Sample.DoesNotExist:
            raise Http404
        datatables_url = api_reverse(
            'samples:multispecimen-data-list', request=self.request, kwargs=self.kwargs
        )
        context.update({
            'sample': sample,
            'experiment_id': sample.site_visit.site.experiment_id,
            'json_context': get_json_context({
                'datatables_url': datatables_url
            }),
            'form_action_url': reverse(
                'samples:multispecimen-images',
                kwargs={'sample_id': sample.id}),
            'container_row_header': get_datatables_container(
                get_datatables_row([
                    'Image',
                    'image_grid',
                    'cropped_to_specimen',
                ]))
        })
        return context

    def form_valid(self, form):
        image_4_by_3 = form.cleaned_data['image_4_by_3']
        json_data = form.cleaned_data['json_data']
        json_crop_ids = form.cleaned_data['json_crop_ids']
        try:
            sample = Sample.objects.user_access(self.request.user).get(id=self.kwargs['sample_id'])
        except Sample.DoesNotExist:
            raise Http404
        if image_4_by_3:
            created_images = 0
            try:
                for f in image_4_by_3:
                    MultiSpecimenImage.objects.create(
                        sample=sample,
                        image=f,
                        image_grid=constants.IMAGE_GRID_CHOICE_4_BY_3,
                        uploaded_by_user=self.request.user
                    )
                    created_images += 1
            except Exception:
                messages.add_message(
                    self.request,
                    messages.ERROR,
                    'Error: An unsupported file may have been selected, please use .jpg or .png')
                created_images = 0
            messages.success(self.request, 'Succesfully added {0} new multi-specimen images'.format(created_images))
        if json_data:
            if not all([isinstance(v, int) for v in json_data['ids']]):
                raise ValidationError(mark_safe('non-integers provided in form as ids'))
            MultiSpecimenImage.objects.user_access(self.request.user).filter(id__in=json_data['ids']).delete()
            messages.warning(self.request, 'Succesfully deleted {0} images'.format(len(json_data['ids'])))
        if json_crop_ids:
            if not all([isinstance(v, int) for v in json_crop_ids['ids']]):
                raise ValidationError(mark_safe('non-integers provided in form as ids'))
            selected_images = MultiSpecimenImage.objects.user_access(self.request.user).filter(
                id__in=json_crop_ids['ids']).exclude(cropped_to_specimen=True)
            prev_cropped = len(json_crop_ids['ids']) - len(selected_images)
            for i in selected_images:
                imgs = crop_img_to_grid(i.image, i.image_grid)
                for cropped_i in imgs:
                    specimen = Specimen.objects.create(
                        sample=sample,
                        created_by_user=self.request.user)
                    SpecimenImage.objects.create(
                        specimen=specimen,
                        image=cropped_i[0],
                        multispecimen_image_uuid=i.uuid,
                        multispecimen_image_index=cropped_i[1],
                        uploaded_by_user=self.request.user
                    )
                i.cropped_to_specimen = True
                i.save()
            messages.warning(self.request, 'Succesfully croped {0} images. {1}'.format(
                len(selected_images),
                str(prev_cropped) + ' images were skipped as already cropped.' if prev_cropped else ''
            ))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('samples:multispecimen-images', kwargs={'sample_id': self.kwargs['sample_id']})
