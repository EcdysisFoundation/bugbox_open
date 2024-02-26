from django.views.generic import TemplateView
from django.contrib.postgres.search import SearchVector
from django.urls import reverse
from django.views.generic.edit import CreateView, UpdateView
from django.forms import modelform_factory, modelformset_factory, inlineformset_factory
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.reverse import reverse as api_reverse
from rest_framework.response import Response


from bugbox3.libs.utilities import get_json_context
from ..libs.ui_helpers import get_formsets_display_control_config
from .models import Experiment, SamplePlan
from .serializers import ExperimentsDatatablesSerializer
from .forms import ExperimentForm, SamplePlanForm
from . import constants


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
        except:
            start = 0
        try:
            length = int(request.query_params.get('length'))
        except:
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

class SpecimensView(TemplateView):
    template_name = 'samples/specimens.html'

class ExperimentSamplePlanCreateView(CreateView):

    form_class = ExperimentForm
    template_name = 'samples/experiment_form.html'
    action = 'create'

    formset_total = 10
    formset_intial = 1

    sample_plan_form_set = inlineformset_factory(Experiment, SamplePlan, form=SamplePlanForm, max_num=formset_total, extra=formset_total)

    def get_context_data(self, **kwargs):
        context = super(ExperimentSamplePlanCreateView, self).get_context_data(**kwargs)
        context['json_context'] = get_json_context(get_formsets_display_control_config(
                    self.formset_total, self.formset_intial))
        if self.request.POST:
            context['formsets'] = self.sample_plan_form_set(self.request.POST)
        else:
            context['formsets'] = self.sample_plan_form_set()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        sample_plans = context['formsets']
        with transaction.atomic():
            self.object = form.save()
            if sample_plans.is_valid():
                sample_plans.instance = self.object
                sample_plans.save()
            else:
                print('ERRORS_sample_plans: ' + str(sample_plans.errors))
        return super(ExperimentSamplePlanCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('samples:experiments')
