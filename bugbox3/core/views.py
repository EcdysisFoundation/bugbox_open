import os
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.postgres.search import SearchVector
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponseRedirect
from django.middleware.csrf import get_token
from django.urls import reverse
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, DeleteView, FormView, UpdateView
from organizations.models import OrganizationUser
from rest_framework.response import Response

from ..libs.utilities import get_json_context, cast_utc_time
from ..samples.constants import (FIELD_SAMPLE_TYPE, FIELD_SITE_HABITAT_TYPE,
                                 FIELD_SITE_TREATMENT, FIELD_SPECIMEN_TAGS,
                                 STITCHER_SAMPLE_TYPES)
from ..samples.models import Sample
from . import constants
from .forms import LookupChoicesForm, StitcherForm
from .models import LookupChoices
from .permissions import IS_ADMIN, IS_RESEARCH, ZEROTIER_USERS
from .stitcher_api import (
    get_root_message,
    get_upload_file,
    patch_upload_file,
    STITCHER_JS_URL_ZEROTIER,
    STITCHER_JS_URL,
    ERROR_MSG_KEY
)


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


class StitcherView(PermissionRequiredMixin, TemplateView):

    permission_required = IS_RESEARCH
    template_name = 'core/stitcher.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        stitcher_url = STITCHER_JS_URL_ZEROTIER if \
            str(self.request.user) in ZEROTIER_USERS else STITCHER_JS_URL
        context.update({
            'json_context': get_json_context({
                'STITCHER_URL': stitcher_url
            })
        })
        root_message = get_root_message()
        if ERROR_MSG_KEY in root_message:
            messages.error(self.request, root_message[ERROR_MSG_KEY])
        return context


class StitcherUpdateView(PermissionRequiredMixin, FormView):

    permission_required = IS_ADMIN

    form_class = StitcherForm
    template_name = 'core/stitcher_form.html'

    def get_context_data(self, **kwargs):
        context = super(StitcherUpdateView, self).get_context_data(**kwargs)
        orgs = OrganizationUser.objects.filter(
            user=self.request.user).values_list(
                'organization_id', flat=True)
        if not orgs:
            raise Http404
        guid = self.kwargs[constants.STITCHER_GUID]
        data = get_upload_file(guid)
        panorma_name = ''
        img_src = ''
        disable_stitching = True
        if constants.STITCHER_PANORAMA_PATH in data.keys():
            if data[constants.STITCHER_PANORAMA_PATH]:
                img_src = data[constants.STITCHER_PANORAMA_PATH].replace('/media/', '/static/')
                panorma_name = os.path.basename(data[constants.STITCHER_PANORAMA_PATH])
            disable_stitching = False if data[constants.STITCHER_APPROVED] is None else True
        stitcher_url = STITCHER_JS_URL_ZEROTIER if \
            str(self.request.user) in ZEROTIER_USERS else STITCHER_JS_URL
        for v in constants.STITCHER_TIMEFIELDS:
            if v in data.keys():
                if data[v]:
                    data[v] = cast_utc_time(data[v])
        # find samples in bugbox
        potential_samples = []
        if constants.STITCHER_UPLOAD_DIR_NAME in data.keys():
            dir_name = data[constants.STITCHER_UPLOAD_DIR_NAME]
            vs = dir_name.split('_')
            if vs:
                samples_w_type = None
                samples_w_transect = None
                sample_ids = None
                samples = Sample.objects.filter(
                    site_visit__site__experiment__organization_id__in=orgs,
                    site_visit__site__site_name__icontains=vs[0]
                )
                if len(vs) >= 2:
                    if vs[1].lower() in STITCHER_SAMPLE_TYPES.keys():
                        sample_type = STITCHER_SAMPLE_TYPES[vs[1].lower()]
                        samples_w_type = samples.filter(sample_type=sample_type)
                    if len(vs) >= 3 and samples_w_type:
                        samples_w_transect = samples_w_type.filter(name_no__icontains=vs[2])
                if samples_w_transect:
                    sample_ids = samples_w_transect.values_list('id', flat=True)
                elif samples_w_type:
                    sample_ids = samples_w_type.values_list('id', flat=True)
                else:
                    sample_ids = samples.values_list('id', flat=True)
                if sample_ids:
                    potential_samples = [
                        (i, reverse('samples:sample', kwargs={'sample_id': i})) for i in sample_ids]
        context.update({
            'data': data,
            'panorma_name': panorma_name,
            'img_src': f'{stitcher_url}{img_src}',
            'potential_samples': potential_samples,
            'form_action_url': reverse(
                'core:stitcher-form', kwargs={'guid': str(guid)}),
            'json_context': get_json_context({
                constants.STITCHER_GUID: guid,
                'STITCHER_URL': stitcher_url,
                'disable_stitching': disable_stitching,
                'csrf_token': get_token(self.request)
            })
        })
        if ERROR_MSG_KEY in data.keys():
            messages.error(self.request, data[ERROR_MSG_KEY])
        return context

    def get_initial(self):
        initial = super().get_initial()
        data = get_upload_file(self.kwargs[constants.STITCHER_GUID])
        if constants.STITCHER_APPROVED in data.keys():
            initial[constants.STITCHER_APPROVED] = data[constants.STITCHER_APPROVED]
        return initial

    def form_valid(self, form):
        print('FORM VALID')
        print(form)
        data = form.cleaned_data
        if data['sample_id']:
            # handle crop and save annotations, and skip other form fields
            try:
                sample = Sample.objects.user_access(
                    self.request.user).get(id=data['sample_id'])
            except Sample.DoesNotExist:
                raise Http404
            print(f'found {sample.id}')
        else:
            if data[constants.STITCHER_APPROVED] == '':
                data[constants.STITCHER_APPROVED] = None
            patch_upload_file(self.kwargs[constants.STITCHER_GUID], data)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('core:stitcher')
