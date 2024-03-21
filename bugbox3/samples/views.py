from django.contrib.postgres.search import SearchVector
from django.db import transaction
from django.forms import inlineformset_factory
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, UpdateView
from rest_framework.response import Response
from rest_framework.reverse import reverse as api_reverse
from rest_framework.viewsets import ReadOnlyModelViewSet

from ..libs.ui_helpers import get_formsets_display_control_config
from ..libs.utilities import get_json_context
from . import constants
from .forms import ExperimentForm, SamplePlanForm, SiteForm, SiteVisitForm
from .models import Experiment, SamplePlan, Site, SiteVisit
from .models_query import get_sample_plan_descriptions
from .serializers import ExperimentsDatatablesSerializer


class ExperimentsDatatablesViewSet(ReadOnlyModelViewSet):
    serializer_class = ExperimentsDatatablesSerializer

    queryset = Experiment.objects.all().order_by(constants.FIELD_NAME)

    def filter_for_datatable(self, queryset):
        # filtering
        search_vector = [constants.FIELD_NAME, constants.FIELD_ABBREVIATION]
        search_query = self.request.query_params.get('search[value]')
        if search_query:
            queryset = queryset.annotate(
                search=SearchVector(*search_vector)
            ).filter(search=search_query)
        return queryset

    def list(self, request, *args, **kwargs):
        draw = request.query_params.get('draw')
        queryset = self.filter_queryset(self.get_queryset())
        recordsTotal = queryset.count()
        filtered_queryset = self.filter_for_datatable(queryset)
        try:
            start = int(request.query_params.get('start'))
        except ValueError:
            start = 0
        try:
            length = int(request.query_params.get('length'))
        except ValueError:
            length = 10
        end = length + start
        serializer = self.get_serializer(filtered_queryset[start:end], many=True)
        response = {
            'draw': draw,
            'recordsTotal': recordsTotal,
            'recordsFiltered': filtered_queryset.count(),
            'data': serializer.data
        }
        return Response(response)


class ExperimentsView(TemplateView):
    template_name = 'samples/experiments.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        experiments_datatables_url = api_reverse('samples:experiment-data-list',
                                                 request=self.request, kwargs=kwargs)
        context['json_context'] = get_json_context({
            'experiments_datatables_url': experiments_datatables_url,
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
        context.update({
            'experiment': experiment,
            'years': years,
            'sample_plan_descriptions': description
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
        experiment = Experiment.objects.all()
        return get_object_or_404(experiment, id=self.kwargs['experiment_id'])

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
            # context['formsets'].full_clean()
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
        context['form_action_url'] = reverse('samples:site-create', kwargs={'experiment_id': self.kwargs['experiment_id']})
        if self.request.POST:
            context['formsets'] = self.form_set(self.request.POST)
        else:
            context['formsets'] = self.form_set()
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
        return super(SiteCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('samples:experiment', kwargs={'experiment_id': self.kwargs['experiment_id']})
