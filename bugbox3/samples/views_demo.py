from django.core.files.storage import default_storage
from django.db import transaction
from django.http import Http404
from django.urls import reverse
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.views.generic import TemplateView, CreateView, UpdateView, FormView
from django.forms import inlineformset_factory
from rest_framework.reverse import reverse as api_reverse

from ..libs.ui_helpers import (
    get_datatables_container, get_datatables_row, get_formsets_display_control_config,
    get_probability, calc_image_height
)
from ..libs.utilities import get_json_context, get_media_url
from .models import Experiment, Site, SiteVisit, Sample, Specimen, SpecimenImage, SamplePlan
from .models_query import get_sample_plan_descriptions
from .forms import ExperimentForm, SiteForm, SiteVisitForm, SamplePlanForm, SampleForm, SpecimenForm, SpecimensWithoutImagesForm
from ..taxonomy import constants as taxa_const
from ..taxonomy.models import Morphospecies
from organizations.models import Organization
from ..core.models import LookupChoices
from bugbox3.samples.utils import resolve_entered_by
from . import constants


DEMO_ORG_NAME = "Bugbox Demo Organization"
DEMO_ORG_SLUG = "bugbox-demo-organization"


def get_demo_organization():
    """Get or create the demo organization."""
    org, created = Organization.objects.get_or_create(
        slug=DEMO_ORG_SLUG,
        defaults={'name': DEMO_ORG_NAME}
    )
    return org


class DemoExperimentsView(TemplateView):
    template_name = 'samples/demo_experiments.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        demo_org = get_demo_organization()
        
        experiments_datatables_url = api_reverse(
            'samples:demo-experiment-data-list',
            request=self.request
        )

        context.update({
            'json_context': get_json_context({
                'experiments_datatables_url': experiments_datatables_url,
                'org_choices': [[demo_org.id, f'Organization: {demo_org.name}']],
                'org_id': demo_org.id,
                'create_experiment_url': reverse('samples:demo-experiment-create'),
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


class DemoExperimentView(TemplateView):
    template_name = 'samples/demo_experiment.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        demo_org = get_demo_organization()
        
        try:
            experiment = Experiment.objects.filter(
                organization=demo_org
            ).get(id=kwargs['experiment_id'])
        except Experiment.DoesNotExist:
            raise Http404

        if experiment.from_year == experiment.to_year:
            years = str(experiment.from_year)
        else:
            years = str(experiment.from_year) + ' - ' + str(experiment.to_year)
        
        description = [v['description'] for v in get_sample_plan_descriptions(experiment.id)]
        sites_datatables_url = api_reverse(
            'samples:demo-site-data-list',
            request=self.request,
            kwargs={'experiment_id': experiment.id}
        )
        experiment_sites = Site.objects.filter(
            experiment_id=experiment.id
        ).order_by(constants.FIELD_SITE_SITE_NAME)

        context.update({
            'experiment': experiment,
            'experiment_sites': experiment_sites,
            'other_experiments': Experiment.objects.filter(organization=demo_org).exclude(
                id=experiment.id).order_by(constants.FIELD_ABBREVIATION),
            'sample_types': LookupChoices.objects.get_field_choices_w_blank(
                experiment.organization_id, constants.FIELD_SAMPLE_TYPE),
            'indices': constants.INDICES_CHOICES,
            'indices_descriptions': constants.INDICES_DESCRIPTIONS,
            'default_indices': constants.INDICES_ALWAYS_INCLUDED,
            'export_types': constants.EXPERIMENT_CSV_EXPORT_CHOICES,
            'years': years,
            'sample_plan_descriptions': description,
            'review_permission': False,
            'skip_morphospecies': '',
            'excluded_from_indices': {'exclude_from_export': [], 'immature': [], 'skipped': [], 'total_count': 0},
            'container_row_header': get_datatables_container(
                get_datatables_row([
                    'Site Name',
                    'State Region',
                    'County Region',
                    'Habitat',
                    'Treatment'
                ])),
            'json_context': get_json_context({
                'sites_datatables_url': sites_datatables_url,
                'experiment': {'id': experiment.id},
                'last_location_exported_file_status': None,
            }),
            'all_habitats': Site.objects.filter(experiment_id=experiment.id).exclude(habitat_type='').values_list('habitat_type', flat=True).distinct(),
            'all_countries': Site.objects.filter(experiment_id=experiment.id).exclude(country='').values_list('country', flat=True).distinct(),
            'all_states': Site.objects.filter(experiment_id=experiment.id).exclude(state_region='').values_list('state_region', flat=True).distinct(),
            'last_exported_file': None,
            'last_exported_file_status': None,
            'last_location_exported_file': None,
            'last_location_exported_file_status': None,
        })
        return context


class DemoSiteView(TemplateView):
    template_name = 'samples/demo_site.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        demo_org = get_demo_organization()
        
        try:
            site = Site.objects.filter(
                experiment__organization=demo_org
            ).get(id=kwargs['site_id'])
        except Site.DoesNotExist:
            raise Http404

        form = SiteForm(instance=site, org_id=site.experiment.organization_id)
        
        visits = SiteVisit.objects.filter(site=site).order_by('-visit_date')
        site_visit_count = visits.count() if visits.exists() else 1

        all_samples = Sample.objects.filter(site_visit__site=site).select_related('site_visit').order_by('site_visit__visit_date', 'name_no')
        
        visits_with_samples = []
        for visit in visits:
            visit_samples = [s for s in all_samples if s.site_visit.id == visit.id]
            if visit_samples:
                visits_with_samples.append((visit, visit_samples))

        form_set = inlineformset_factory(Site, SiteVisit, form=SiteVisitForm, max_num=20, extra=0)
        formsets = form_set(instance=site)

        context.update({
            'form': form,
            'site_id': site.id,
            'action': 'view',
            'visits': visits,
            'visits_with_samples': visits_with_samples,
            'formsets': formsets,
            'experiment_details': {
                'experiment': site.experiment,
                'plans': get_sample_plan_descriptions(site.experiment.id)
            },
            'json_context': get_json_context(get_formsets_display_control_config(20, site_visit_count)),
            'form_action_url': '#',
            'has_related_data': [
                i.visit_date for i in visits if i.has_related_data
            ],
            'demo_org': demo_org,
        })
        return context


class DemoSampleView(TemplateView):
    template_name = 'samples/demo_sample.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        demo_org = get_demo_organization()
        
        try:
            sample = Sample.objects.filter(
                site_visit__site__experiment__organization=demo_org
            ).get(id=kwargs['sample_id'])
        except Sample.DoesNotExist:
            raise Http404(f"Sample {kwargs['sample_id']} not found in demo organization. Available demo samples: {list(Sample.objects.filter(site_visit__site__experiment__organization=demo_org).values_list('id', flat=True))}")

        specimens_datatables_url = api_reverse(
            'samples:demo-specimen-data-list',
            request=self.request,
            kwargs={'sample_id': sample.id}
        )

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
            sample.site_visit.site.experiment.organization_id, constants.FIELD_SAMPLE_TYPE).get(
            sample.sample_type, sample.sample_type) if sample.sample_type in LookupChoices.objects.get_field_dict_w_blank(
            sample.site_visit.site.experiment.organization_id, constants.FIELD_SAMPLE_TYPE).keys() else sample.sample_type

        has_data = sample.specimen_set.exists() or (sample.image and default_storage.exists(sample.image.name))
        entered_by = resolve_entered_by(sample)

        context.update({
            'sample_info': {
                'sample_id': sample.id,
                'experiment_name': sample.site_visit.site.experiment.name,
                'experiment_id': sample.site_visit.site.experiment_id,
                'organization_id': sample.site_visit.site.experiment.organization_id,
                'uuid': sample.uuid,
                'site': sample.site_visit.site.site_name,
                'country': sample.site_visit.site.country,
                'state': sample.site_visit.site.state_region,
                'county': sample.site_visit.site.county_region,
                'habitat': sample.site_visit.site.habitat_type,
                'treatment': sample.site_visit.site.treatment,
                'visit_date': sample.site_visit.visit_date.strftime("%d-%b-%Y"),
                'sample_type': sample_type,
                'name_no': sample.name_no,
                'entered_by': entered_by,
                'notes': sample.notes,
                'completed': sample.completed,
                'img_thumbnail': img_thumbnail,
                'has_data': has_data
            },
            'review_permission': False,
            'container_row_header': get_datatables_container(
                get_datatables_row([
                    'Image',
                    'Partial<br/>Count',
                    'Classification',
                    'Probability<br/>(Model)',
                ])),
            'sample_container_row_header': get_datatables_container(
                get_datatables_row([
                    'Site',
                    'Date',
                    'Type',
                    'Name',
                ])),
            'json_context': get_json_context({
                'specimen_datatables_url': specimens_datatables_url,
                'sample': {'id': sample.id},
            }),
            'form_action_url': '#',
            'demo_org': demo_org,
        })
        return context


class DemoSpecimenView(TemplateView):
    template_name = 'samples/demo_specimen.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        demo_org = get_demo_organization()
        
        try:
            specimen = Specimen.objects.filter(
                sample__site_visit__site__experiment__organization=demo_org
            ).get(id=kwargs.get('id') or kwargs.get('specimen_id'))
        except Specimen.DoesNotExist:
            raise Http404

        s_images = SpecimenImage.objects.filter(
            specimen=specimen,
            public_image=True
        ).order_by('-primary_image', 'date_added')
        
        if s_images:
            if len(s_images) > 1:
                image_set_large = [
                    {'path': get_media_url(
                        i.image_thumbnail_large, i.public_image), 'id': i.id} 
                    for i in s_images if i.image_thumbnail_large
                ]
                if not image_set_large:
                    image_set_large = [{
                        'path': get_media_url(s_images[0].image, s_images[0].public_image),
                    }]
                image_set_small = [
                    {
                        'path': get_media_url(i.image_thumbnail_medium, i.public_image),
                        'width': i.image_thumbnail_medium_width * 0.5 if i.image_thumbnail_medium_width else None,
                        'height': i.image_thumbnail_medium_height * 0.5 if i.image_thumbnail_medium_height else None,
                        'id': i.id
                    } for i in s_images if i.image_thumbnail_medium and i.id != image_set_large[0].get('id')
                ]

                context.update({
                    'image_set_small': image_set_small,
                    'image_set_large': image_set_large,
                })
            else:
                i_public_image = s_images[0].public_image
                if s_images[0].image_thumbnail_large:
                    i = s_images[0].image_thumbnail_large
                    img_width = s_images[0].image_thumbnail_large_width
                    img_height = s_images[0].image_thumbnail_large_height
                else:
                    i = s_images[0].image
                    img_width = s_images[0].image_width
                    img_height = s_images[0].image_height
                single_image = {
                    'path': get_media_url(i, i_public_image),
                    'width': img_width,
                    'height': img_height,
                }
                context.update({'single_image': single_image})

        selected_classification = (
            specimen.ai_classification
            if not specimen.classification and specimen.acceptance != 2
            else specimen.classification
        )

        acceptance = ''
        if specimen.acceptance == 1:
            acceptance = 'Confirmed'
        elif specimen.acceptance == 2:
            acceptance = 'Rejected'
        else:
            acceptance = 'Pending'

        ai_classification = specimen.ai_classification
        if not ai_classification:
            class MockAI:
                name = None
            ai_classification = MockAI()
        
        context.update({
            'specimen': specimen,
            'selected_classification': selected_classification,
            'verified_classification': specimen.classification,
            'ai_classification': ai_classification,
            'probability': get_probability(specimen),
            'acceptance': acceptance,
            'acceptance_choices': constants.ACCEPTANCE_CHOICES,
            'review_permission': True,
            'form_action_url': '#',
            'json_context': get_json_context({}),
            'demo_org': demo_org,
        })
        return context


class DemoExperimentCreateView(CreateView):
    form_class = ExperimentForm
    template_name = 'samples/experiment_form.html'
    action = 'create'

    formset_total = 10
    formset_initial = 1

    sample_plan_form_set = inlineformset_factory(
        Experiment, SamplePlan, form=SamplePlanForm, max_num=formset_total, extra=formset_total)

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        demo_org = get_demo_organization()
        form.fields['organization'].choices = [(demo_org.id, demo_org.name)]
        form.fields['organization'].initial = demo_org.id
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        demo_org = get_demo_organization()

        context['json_context'] = get_json_context(get_formsets_display_control_config(
            self.formset_total, self.formset_initial))
        context['form_action_url'] = reverse('samples:demo-experiment-create')
        if self.request.POST:
            context['formsets'] = self.sample_plan_form_set(
                self.request.POST, form_kwargs={'org_id': demo_org.id})
        else:
            context['formsets'] = self.sample_plan_form_set(
                form_kwargs={'org_id': demo_org.id})
        return context

    def form_valid(self, form):
        demo_org = get_demo_organization()
        form.instance.organization = demo_org
        context = self.get_context_data()
        formsets = context['formsets']
        with transaction.atomic():
            self.object = form.save()
            if formsets.is_valid():
                formsets.instance = self.object
                formsets.save()
            else:
                print('ERRORS_formsets: ' + str(formsets.errors))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('samples:demo-experiment', kwargs={'experiment_id': self.object.id})


class DemoSiteCreateView(CreateView):
    form_class = SiteForm
    template_name = 'samples/site_form.html'
    action = 'create'

    formset_total = 10

    form_set = inlineformset_factory(Site, SiteVisit, form=SiteVisitForm, max_num=formset_total, extra=formset_total)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        demo_org = get_demo_organization()
        kwargs['org_id'] = demo_org.id
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        demo_org = get_demo_organization()
        
        try:
            experiment = Experiment.objects.filter(
                organization=demo_org
            ).get(id=self.kwargs['experiment_id'])
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
                'samples:demo-site-create', kwargs={'experiment_id': self.kwargs['experiment_id']})
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
                if hasattr(i, 'created_by_user_id'):
                    i.created_by_user_id = None
                i.save()
            formsets.save()
        else:
            print('ERRORS_formsets: ' + str(formsets.errors))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('samples:demo-experiment', kwargs={'experiment_id': self.kwargs['experiment_id']})


class DemoSampleUpdateView(UpdateView):
    form_class = SampleForm
    template_name = 'samples/sample_form.html'
    action = 'update'

    def get_object(self, queryset=None):
        demo_org = get_demo_organization()
        try:
            return Sample.objects.filter(
                site_visit__site__experiment__organization=demo_org
            ).get(id=self.kwargs['sample_id'])
        except Sample.DoesNotExist:
            raise Http404

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        demo_org = get_demo_organization()
        kwargs['org_id'] = demo_org.id
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_action_url'] = reverse('samples:demo-sample-update', kwargs={'sample_id': self.kwargs['sample_id']})
        return context

    def get_success_url(self):
        return reverse('samples:demo-sample', kwargs={'sample_id': self.kwargs['sample_id']})


class DemoSpecimenCreateView(CreateView):
    form_class = SpecimenForm
    template_name = 'samples/specimen_create.html'
    action = 'create'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        demo_org = get_demo_organization()
        try:
            sample = Sample.objects.filter(
                site_visit__site__experiment__organization=demo_org
            ).get(id=self.kwargs['sample_id'])
        except Sample.DoesNotExist:
            raise Http404
        kwargs['org_id'] = demo_org.id
        kwargs['review_permission'] = False
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        demo_org = get_demo_organization()
        try:
            sample = Sample.objects.filter(
                site_visit__site__experiment__organization=demo_org
            ).get(id=self.kwargs['sample_id'])
        except Sample.DoesNotExist:
            raise Http404
        context.update({
            'form_action_url': reverse('samples:demo-specimen-create', kwargs={'sample_id': sample.id}),
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
        demo_org = get_demo_organization()
        try:
            sample = Sample.objects.filter(
                site_visit__site__experiment__organization=demo_org
            ).get(id=self.kwargs['sample_id'])
        except Sample.DoesNotExist:
            raise Http404
        if not form.instance.classification:
            messages.error(
                self.request, 'A verified classification is required, please select one to create.')
            return redirect('samples:demo-specimen-create', sample_id=sample.id)
        form.instance.sample_id = sample.id
        form.instance.created_by_user_id = None
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('samples:demo-specimen', kwargs={'id': self.object.id})


class DemoSpecimensWithoutImagesFormView(FormView):
    form_class = SpecimensWithoutImagesForm
    template_name = 'samples/specimens_wo_images.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        demo_org = get_demo_organization()
        try:
            sample = Sample.objects.filter(
                site_visit__site__experiment__organization=demo_org
            ).get(id=self.kwargs['sample_id'])
        except Sample.DoesNotExist:
            raise Http404
        morpho_names = [v[taxa_const.FIELD_MORPHO_NAME] for v in taxa_const.SKIP_MORPHOSPECIES]
        existing_names = []
        for m in morpho_names:
            if Specimen.objects.filter(classification__name=m, sample_id=sample.id):
                existing_names.append(m)
        use_names = [v for v in morpho_names if v not in existing_names]
        sample_type = LookupChoices.objects.get_field_dict_w_blank(
            demo_org.id,
            constants.FIELD_SAMPLE_TYPE).get(sample.sample_type, sample.sample_type) \
            if sample.sample_type in LookupChoices.objects.get_field_dict_w_blank(
            demo_org.id,
            constants.FIELD_SAMPLE_TYPE).keys() \
            else sample.sample_type
        context.update({
            'morpho_names': ', '.join(morpho_names),
            'existing_names': ', '.join(existing_names),
            'use_names': use_names,
            'sample_link': reverse(
                'samples:demo-sample', kwargs={'sample_id': self.kwargs['sample_id']}),
            'experiment': sample.site_visit.site.experiment.name,
            'experiment_id': sample.site_visit.site.experiment.id,
            'site_name': sample.site_visit.site.site_name,
            'visit_date': sample.site_visit.visit_date.strftime("%d-%b-%Y"),
            'sample_type': sample_type,
            'name_no': sample.name_no,
            'form_action_url': reverse(
                'samples:demo-specimens-wo-img', kwargs={'sample_id': self.kwargs['sample_id']})
        })
        return context

    def form_valid(self, form):
        demo_org = get_demo_organization()
        try:
            sample = Sample.objects.filter(
                site_visit__site__experiment__organization=demo_org
            ).get(id=self.kwargs['sample_id'])
        except Sample.DoesNotExist:
            raise Http404
        entered_names = []
        for v in taxa_const.SKIP_MORPHOSPECIES:
            name = v[taxa_const.FIELD_MORPHO_NAME]
            if name in form.cleaned_data:
                if form.cleaned_data[name]:
                    morphospecies = get_object_or_404(Morphospecies, name=name)
                    Specimen.objects.create(
                        sample=sample,
                        classification=morphospecies,
                        created_by_user=None,
                        partial_count=form.cleaned_data[name]
                    )
                    entered_names.append(name)
        messages.success(
            self.request, 'Successfully entered counts for {0}'.format(
                ', '.join(entered_names)
            ))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('samples:demo-sample', kwargs={'sample_id': self.kwargs['sample_id']})
