import os
from django.http import Http404
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse
from django.views.generic import FormView, TemplateView
from django.contrib import messages
from organizations.models import OrganizationUser

from bugbox3.samples.models import Sample
from bugbox3.samples.constants import STITCHER_SAMPLE_TYPES
from bugbox3.libs.utilities import get_json_context, cast_utc_time
from .permissions import IS_RESEARCH, ZEROTIER_USERS, IS_ADMIN
from .forms import StitcherForm
from .stitcher_api import (
    get_root_message,
    get_upload_file,
    patch_upload_file,
    STITCHER_JS_URL_ZEROTIER,
    STITCHER_JS_URL,
    ERROR_MSG_KEY
)
from . import constants
# from .stitcher_utils import convert_ls_to_coco_to_pil, crop_and_save_images


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
            'first_potential_sample': potential_samples[0][0] if potential_samples else None,
            'form_action_url': reverse(
                'core:stitcher-form', kwargs={'guid': str(guid)}),
            'form_iden_crop_save': constants.STITCHER_FORM_CROPSAVE,
            'disable_crop_save': False if data[constants.STITCHER_APPROVED] else True,
            'json_context': get_json_context({
                constants.STITCHER_GUID: guid,
                'STITCHER_URL': stitcher_url,
                'disable_stitching': disable_stitching
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

    def form_invalid(self, form):
        print('FORM INVALID')
        return super().form_invalid(form)

    def form_valid(self, form):
        data = form.cleaned_data
        if data['form_ident'] == constants.STITCHER_FORM_CROPSAVE:
            if data['sample_id']:
                try:
                    sample = Sample.objects.user_access(
                        self.request.user).get(id=data['sample_id'])
                except Sample.DoesNotExist:
                    raise Http404
                messages.success(
                   self.request, f'Succesfully sent sample_id {data['sample_id']}'
                )
                messages.warning(
                   self.request, 'Crop and Save is not implemented yet, so nothing really happened.'
                )
        elif data['form_ident'] == constants.STITCHER_FORM_DEFAULT:
            approved = data[constants.STITCHER_APPROVED]
            if approved == '':
                approved = None
            patch_upload_file(self.kwargs[constants.STITCHER_GUID], data)
            messages.success(
                self.request, f'Succesfully set approved to {approved}'
            )
        else:
            messages.error(self.request, 'There was an error in form submission.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('core:stitcher')
