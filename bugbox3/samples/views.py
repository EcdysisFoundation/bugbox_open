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
from .models import Experiment, SamplePlan
from .serializers import ExperimentsDatatablesSerializer
from .forms import (ExperimentForm, SamplePlanFormSetHelper, ExperimentForm2,
                    SamplePlanFormSet, ExperimentForm3, SamplePlanForm3)
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
        #context['experiment_create_url'] = reverse('samples:experimenent-create', kwargs=kwargs)
        context['json_context'] = get_json_context({
            'experiments_datatables_url': experiments_datatables_url,
        })
        return context

class SpecimensView(TemplateView):
    template_name = 'samples/specimens.html'


class ExperimentCreateView(CreateView):
    template_name = 'samples/experiment_form.html'
    action = 'create'

    def get_form_class(self):
        return modelform_factory(Experiment, ExperimentForm, 
                                 constants.FORM_FIELDS_EXPERIMENT)


def experiment_create_view(request):
    SamplePlanFormSet = modelformset_factory(SamplePlan,
                                             fields=constants.FORM_FIELDS_SAMPLE_PLAN)
    helper = SamplePlanFormSetHelper()
    #helper.add_input(Submit("submit", "Save"))
    if request.method == 'POST':
        formset = SamplePlanFormSet(request.POST, request.FILES)
        if formset.is_valid():
            formset.save()
            # do something.
    else:
        formset = SamplePlanFormSet()
    return render(request, 'samples/experiment_sample_plan_form.html', {'formset': formset, 'helper': helper})


class ExperimentSamplePlan():
    form_class = ExperimentForm2
    model = Experiment
    template_name = 'samples/experiment_sample_plan.html'

    def form_valid(self, form):
        named_formsets = self.get_named_formsets()
        if not all((x.is_valid() for x in named_formsets.values())):
            return self.render_to_response(self.get_context_data(form=form))

        self.object = form.save()

        # for every formset, attempt to find a specific formset save function
        # otherwise, just save.
        for name, formset in named_formsets.items():
            formset_save_func = getattr(self, 'formset_{0}_valid'.format(name), None)
            if formset_save_func is not None:
                formset_save_func(formset)
            else:
                formset.save()
        return redirect('samples:experiments')
    
    def formset_sample_plan_valid(self, formset):
        
        sample_plans = formset.save(commit=False)
        
        for obj in formset.deleted_objects:
            obj.delete()
        for sample_plan in sample_plans:
            sample_plan.experiment = self.object
            sample_plan.save()


class ExperimentCreateView2(ExperimentSamplePlan, CreateView):

    def get_context_data(self, **kwargs):
        context = super(ExperimentCreateView2, self).get_context_data(**kwargs)
        context['named_formsets'] = self.get_named_formsets()
        return context
    
    def get_named_formsets(self):
        if self.request.method == 'GET':
            return {
                'sample_plans': SamplePlanFormSet(prefix='sample_plans'),
            }
        else:
            return {
                'sample_plans': SamplePlanFormSet(self.request.POST or None, self.request.FILES or None, prefix='sample_plans'),
            }


class ExperimentUpdateView(ExperimentSamplePlan, UpdateView):

    def get_context_data(self, **kwargs):
        context = super(ExperimentUpdateView, self).get_context_data(**kwargs)
        context['named_formsets'] = self.get_named_formsets()
        return context

    def get_named_formsets(self):
        return {
            'sample_plans': SamplePlanFormSet(self.request.POST or None, self.request.FILES or None, instance=self.object, prefix='sample_plans'),
        }

def delete_sample_plan(request, pk):
    try:
        sample_plan = SamplePlan.objects.get(id=pk)
    except SamplePlan.DoesNotExist:
        messages.success(
            request, 'Object Does not exit'
            )
        return redirect('samples:experiment_update', pk=sample_plan.experiment.id)

    sample_plan.delete()
    messages.success(
            request, 'Image deleted successfully'
            )
    return redirect('samples:experiment_udpate', pk=sample_plan.experiment.id)


class ExperimentSamplePlanCreateView(CreateView):

    form_class = ExperimentForm3
    template_name = 'samples/experiment_form_3.html'
    action = 'create'

    SamplePlanFormSet3 = inlineformset_factory(Experiment, SamplePlan, form=SamplePlanForm3, extra=2)

    def get_context_data(self, **kwargs):
        data = super(ExperimentSamplePlanCreateView, self).get_context_data(**kwargs)
        if self.request.POST:
            data['sample_plans'] = self.SamplePlanFormSet3(self.request.POST)
        else:
            data['sample_plans'] = self.SamplePlanFormSet3()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        sample_plans = context['sample_plans']
        with transaction.atomic():
            form.instance.created_by = self.request.user
            form.instance.updated_by = self.request.user
            self.object = form.save()
            if sample_plans.is_valid():
                sample_plans.instance = self.object
                sample_plans.save()
        return super(ExperimentSamplePlanCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('samples:experiments')
