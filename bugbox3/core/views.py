from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.postgres.search import SearchVector
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from rest_framework.response import Response

from ..samples.constants import (FIELD_SAMPLE_TYPE, FIELD_SITE_HABITAT_TYPE,
                                 FIELD_SITE_TREATMENT, FIELD_SPECIMEN_TAGS)
from . import constants
from .forms import LookupChoicesForm
from .models import LookupChoices
from .permissions import IS_ADMIN


class DatatablesModelViewSetMixin:
    """
    For use with ViewSet such as ReadOnlyModelViewSet and datatables.
    In ViewSet, proved a serializer_class and a get_queryset or queryset
    and optionally a search_vector for filtering.
    """

    search_vector = []

    def filter_for_datatable(self, queryset):
        if self.search_vector:
            search_query = self.request.query_params.get('search[value]')
            if search_query:
                queryset = queryset.annotate(
                    search=SearchVector(*self.search_vector)
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


class LookupChoicesView(PermissionRequiredMixin, TemplateView):

    permission_required = IS_ADMIN

    template_name = 'core/lookup_choices.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            FIELD_SITE_HABITAT_TYPE: LookupChoices.objects.get_field_choices_w_id(
                FIELD_SITE_HABITAT_TYPE),
            FIELD_SITE_TREATMENT: LookupChoices.objects.get_field_choices_w_id(
                FIELD_SITE_TREATMENT),
            FIELD_SPECIMEN_TAGS: LookupChoices.objects.get_field_choices_w_id(
                FIELD_SPECIMEN_TAGS),
            FIELD_SAMPLE_TYPE: LookupChoices.objects.get_field_choices_w_id(
                FIELD_SAMPLE_TYPE)
        })
        return context


class LookupChoicesCreateView(PermissionRequiredMixin, CreateView):

    permission_required = IS_ADMIN

    form_class = LookupChoicesForm
    template_name = 'core/lookup_choices_form.html'
    action = 'create'

    def get_context_data(self, **kwargs):
        context = super(LookupChoicesCreateView, self).get_context_data(**kwargs)
        field = None
        if self.kwargs[constants.FIELD_FIELD] in constants.VALID_LOOKUP_FIELDS:
            field = self.kwargs[constants.FIELD_FIELD]
        if not field:
            raise Http404('Page not found')
        context.update({
            constants.FIELD_FIELD: field,
            'form_action_url': reverse('core:lookup-choices-create', kwargs={constants.FIELD_FIELD: field}),
        })
        return context

    def form_valid(self, form):
        field = None
        if self.kwargs[constants.FIELD_FIELD] in constants.VALID_LOOKUP_FIELDS:
            field = self.kwargs[constants.FIELD_FIELD]
        if not field:
            raise Http404('Page not found')
        form.instance.field = self.kwargs[constants.FIELD_FIELD]
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('core:lookup-choices')


class LookupChoicesUpdateView(PermissionRequiredMixin, UpdateView):

    permission_required = IS_ADMIN

    form_class = LookupChoicesForm
    template_name = 'core/lookup_choices_form.html'
    action = 'update'

    def get_object(self, queryset=None):
        return get_object_or_404(LookupChoices, id=self.kwargs['id'])

    def get_context_data(self, **kwargs):
        context = super(LookupChoicesUpdateView, self).get_context_data(**kwargs)
        choice = get_object_or_404(LookupChoices, id=self.kwargs['id'])
        context.update({
            'field': choice.field,
            'form_action_url': reverse('core:lookup-choices-update', kwargs={'id': choice.id}),
            'delete_button': '<a href="{0}" class="btn btn-danger" role="button">Delete</a>'.format(
                reverse('core:lookup-choices-delete', kwargs={'id': choice.id})
            )
        })
        return context

    def get_success_url(self):
        return reverse('core:lookup-choices')


class LookupChoicesDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = IS_ADMIN

    model = LookupChoices
    template_name = 'samples/confirm_delete.html'

    def get_object(self, queryset=None):
        return get_object_or_404(LookupChoices, id=self.kwargs['id'])

    def get_success_url(self):
        return reverse('core:lookup-choices')
