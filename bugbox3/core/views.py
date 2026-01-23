from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.postgres.search import SearchVector
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from organizations.models import OrganizationUser
from rest_framework.response import Response

from ..samples.constants import FIELD_SAMPLE_TYPE, FIELD_SITE_HABITAT_TYPE, FIELD_SITE_TREATMENT, FIELD_SPECIMEN_TAGS
from ..taxonomy.constants import FIELD_MORPHO_TAGS_LOOKUP
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
        except (TypeError, ValueError):
            start = 0
        try:
            length = int(request.query_params.get('length'))
        except (TypeError, ValueError):
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
        orgs = OrganizationUser.objects.filter(
            user=self.request.user).values(
                'organization_id', 'organization__name').order_by('organization_id')
        org_choices = [(o['organization_id'], o['organization__name']) for o in orgs]
        if (self.kwargs['org_id'] not in [o[0] for o in org_choices]
                and self.kwargs['org_id'] != 0) \
                or not org_choices:
            raise Http404
        if self.kwargs['org_id'] == 0:
            selected_org_name = org_choices[0][1]
            selected_org_id = org_choices[0][0]
        else:
            selected_org_name = [o[1] for o in org_choices if o[0] == self.kwargs['org_id']][0]
            selected_org_id = [o[0] for o in org_choices if o[0] == self.kwargs['org_id']][0]

        context.update({
            FIELD_SITE_HABITAT_TYPE: LookupChoices.objects.get_field_choices_w_id(
                selected_org_id, FIELD_SITE_HABITAT_TYPE),
            FIELD_SITE_TREATMENT: LookupChoices.objects.get_field_choices_w_id(
                selected_org_id, FIELD_SITE_TREATMENT),
            FIELD_SPECIMEN_TAGS: LookupChoices.objects.get_field_choices_w_id(
                selected_org_id, FIELD_SPECIMEN_TAGS),
            FIELD_SAMPLE_TYPE: LookupChoices.objects.get_field_choices_w_id(
                selected_org_id, FIELD_SAMPLE_TYPE),
            FIELD_MORPHO_TAGS_LOOKUP: LookupChoices.objects.get_field_choices_w_id(
                selected_org_id, FIELD_MORPHO_TAGS_LOOKUP),
            'org_choices': org_choices,
            'selected_org_name': selected_org_name,
            'selected_org_id': selected_org_id
        })
        return context


class LookupChoicesCreateView(PermissionRequiredMixin, CreateView):

    permission_required = IS_ADMIN

    form_class = LookupChoicesForm
    template_name = 'core/lookup_choices_form.html'
    action = 'create'

    def get_context_data(self, **kwargs):
        context = super(LookupChoicesCreateView, self).get_context_data(**kwargs)
        try:
            self.org = OrganizationUser.objects.get(
                user=self.request.user,
                organization_id=self.kwargs['org_id'])
        except OrganizationUser.DoesNotExist:
            raise Http404
        field = None
        if self.kwargs[constants.FIELD_FIELD] in constants.VALID_LOOKUP_FIELDS:
            field = self.kwargs[constants.FIELD_FIELD]
        if not field:
            raise Http404('Page not found')
        context.update({
            constants.FIELD_FIELD: field,
            'organization': self.org.organization.name,
            'form_action_url': reverse(
                'core:lookup-choices-create',
                kwargs={constants.FIELD_FIELD: field, 'org_id': self.kwargs['org_id']}),
        })
        return context

    def form_valid(self, form):
        self.get_context_data()
        field = None
        if self.kwargs[constants.FIELD_FIELD] in constants.VALID_LOOKUP_FIELDS:
            field = self.kwargs[constants.FIELD_FIELD]
        if not field:
            raise Http404('Page not found')
        form.instance.field = self.kwargs[constants.FIELD_FIELD]
        form.instance.organization = self.org.organization
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('core:lookup-choices', kwargs={'org_id': self.org.organization_id})


class LookupChoicesUpdateView(PermissionRequiredMixin, UpdateView):

    permission_required = IS_ADMIN

    form_class = LookupChoicesForm
    template_name = 'core/lookup_choices_form.html'
    action = 'update'

    def get_object(self, queryset=None):
        try:
            return LookupChoices.objects.user_access(self.request.user).get(id=self.kwargs['id'])
        except LookupChoices.DoesNotExist:
            raise Http404

    def get_context_data(self, **kwargs):
        context = super(LookupChoicesUpdateView, self).get_context_data(**kwargs)
        context.update({
            'field': self.object.field,
            'form_action_url': reverse('core:lookup-choices-update', kwargs={'id': self.object.id}),
            'delete_button': '<a href="{0}" class="btn btn-danger" role="button">Delete</a>'.format(
                reverse('core:lookup-choices-delete', kwargs={'id': self.object.id})
            )
        })
        return context

    def get_success_url(self):
        return reverse('core:lookup-choices', kwargs={'org_id': self.object.organization_id})


class LookupChoicesDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = IS_ADMIN

    model = LookupChoices
    template_name = 'samples/confirm_delete.html'

    def get_object(self, queryset=None):
        try:
            return LookupChoices.objects.user_access(self.request.user).get(id=self.kwargs['id'])
        except LookupChoices.DoesNotExist:
            raise Http404

    def get_success_url(self):
        return reverse('core:lookup-choices', kwargs={'org_id': self.object.organization_id})


class OrgMembersView(PermissionRequiredMixin, TemplateView):

    permission_required = IS_ADMIN

    template_name = 'core/org_members.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        orgs = OrganizationUser.objects.filter(
            user=self.request.user).values(
                'organization_id', 'organization__name').order_by('organization_id')
        org_choices = [(o['organization_id'], o['organization__name']) for o in orgs]
        if (self.kwargs['org_id'] not in [o[0] for o in org_choices]
                and self.kwargs['org_id'] != 0) \
                or not org_choices:
            raise Http404
        if self.kwargs['org_id'] == 0:
            selected_org_name = org_choices[0][1]
            selected_org_id = org_choices[0][0]
        else:
            selected_org_name = [o[1] for o in org_choices if o[0] == self.kwargs['org_id']][0]
            selected_org_id = [o[0] for o in org_choices if o[0] == self.kwargs['org_id']][0]
        users = OrganizationUser.objects.filter(
            organization_id=selected_org_id).order_by('-is_admin', 'user__username')
        u = OrganizationUser.objects.get(user_id=self.request.user, organization_id=selected_org_id)
        context.update({
            'org_choices': org_choices,
            'selected_org_name': selected_org_name,
            'selected_org_id': selected_org_id,
            'users': users,
            'is_admin': u.is_admin
        })
        return context


class OrgMemberDeleteView(PermissionRequiredMixin, DeleteView):

    permission_required = IS_ADMIN

    model = OrganizationUser
    template_name = 'core/confirm_delete.html'

    def get_object(self, queryset=None):
        try:
            u = OrganizationUser.objects.get(user_id=self.request.user, organization_id=self.kwargs['org_id'])
        except OrganizationUser.DoesNotExist:
            raise Http404
        if not u.is_admin:
            raise PermissionDenied
        try:
            return OrganizationUser.objects.get(id=self.kwargs['id'])
        except OrganizationUser.DoesNotExist:
            raise Http404

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'object_name': 'Member',
            'object_description': self.object.user.name
        })
        return context

    def form_valid(self, form):
        obj = self.get_object()
        user = obj.user
        super().form_valid(form)
        other_memberships = OrganizationUser.objects.filter(
            user_id=obj.user.id)
        if not len(other_memberships):
            # clear all permissions when there are no other memberships
            user.groups.clear()
            user.user_permissions.clear()
        messages.success(
            self.request, 'Succesfully removed member {0}'.format(user.name))
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('core:org-members', kwargs={'org_id': self.kwargs['org_id']})
