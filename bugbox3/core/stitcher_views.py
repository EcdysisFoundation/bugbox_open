import os

import requests
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.files.base import ContentFile
from django.db import transaction
from django.db.utils import IntegrityError
from django.http import Http404, JsonResponse
from django.urls import reverse
from django.views.generic import FormView, TemplateView, View
from organizations.models import OrganizationUser

from bugbox3.libs.utilities import cast_utc_time, get_json_context
from bugbox3.samples.constants import STITCHER_SAMPLE_TYPES
from bugbox3.samples.models import MultiSpecimenImage, Sample
from bugbox3.samples.tasks import crop_panorama_segmentation

from . import constants
from .forms import StitcherDeleteForm, StitcherForm
from .permissions import IS_ADMIN, IS_RESEARCH, ZEROTIER_USERS
from .shimsy_api import create_rescan_request
from .stitcher_api import (
    ERROR_MSG_KEY,
    STITCHER_JS_URL,
    STITCHER_JS_URL_ZEROTIER,
    STITCHER_FLOWER_URL,
    STITCHER_URL,
    cleanup_matching_retake_records,
    delete_upload_file,
    get_root_message,
    get_stitcher_stats,
    get_upload_file,
    patch_upload_file,
)


class StitcherView(PermissionRequiredMixin, TemplateView):

    permission_required = IS_RESEARCH
    template_name = 'core/stitcher.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        stitcher_url = STITCHER_JS_URL_ZEROTIER if \
            str(self.request.user) in ZEROTIER_USERS else STITCHER_JS_URL
        stats = get_stitcher_stats()
        if constants.STITCHER_STATS_LS_PROJECTS in stats.keys():
            ls_projects_choices = [(v[0], f'{v[0]} ({v[1]})')
                                   for v in stats[constants.STITCHER_STATS_LS_PROJECTS]]
        else:
            ls_projects_choices = [(None, None)]

        context.update({
            'stats': stats,
            'STITCHER_FLOWER_URL': STITCHER_FLOWER_URL,
            'json_context': get_json_context({
                'STITCHER_URL': stitcher_url,
                'ls_projects_choices': ls_projects_choices,
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

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        orgs = OrganizationUser.objects.filter(
            user=self.request.user).values_list(
                'organization_id', flat=True)
        if not orgs:
            raise Http404
        guid = self.kwargs[constants.STITCHER_GUID]
        self.guid = guid
        upload_file_response = get_upload_file(guid)
        self.data = upload_file_response[constants.STITCHER_UPLOADFILE_KEY] \
            if constants.STITCHER_UPLOADFILE_KEY in upload_file_response.keys() else upload_file_response
        self.task_response = upload_file_response[constants.STITCHER_TASK_KEY] \
            if constants.STITCHER_TASK_KEY in upload_file_response.keys() else None
        self.stitcher_url = STITCHER_URL
        self.stitcher_js_url = STITCHER_JS_URL_ZEROTIER if \
            str(self.request.user) in ZEROTIER_USERS else STITCHER_JS_URL
        self.panorama_name = ''
        self.img_src = ''
        self.thumbnail_src = None
        self.label_src = f'/static/{self.guid}/{constants.STITCHER_LABEL_IMG}'
        self.nota_sample = None
        self.omit_from_training = None
        if constants.STITCHER_PANORAMA_PATH in self.data.keys():
            if self.data[constants.STITCHER_PANORAMA_PATH]:
                self.img_src = self.data[constants.STITCHER_PANORAMA_PATH].replace('/media/', '/static/')
                if self.data[constants.STITCHER_PANORAMA_THUMBNAIL_PATH]:
                    self.thumbnail_src = self.data[constants.STITCHER_PANORAMA_THUMBNAIL_PATH].replace(
                        '/media/', '/static/')
                self.panorama_name = os.path.basename(self.data[constants.STITCHER_PANORAMA_PATH])
        if constants.STITCHER_NOTA_SAMPLE in self.data.keys():
            self.nota_sample = self.data[constants.STITCHER_NOTA_SAMPLE]
        if constants.STITCHER_OMIT_FROM_TRAINING in self.data.keys():
            self.omit_from_training = self.data[constants.STITCHER_OMIT_FROM_TRAINING]
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(StitcherUpdateView, self).get_context_data(**kwargs)
        orgs = OrganizationUser.objects.filter(
            user=self.request.user).values_list(
                'organization_id', flat=True)
        if not orgs:
            raise Http404
        disable_stitching = True
        disable_crop_save = True
        disable_delete = False
        potential_samples = []
        first_potential_sample = None
        if ERROR_MSG_KEY not in self.data.keys():
            for v in constants.STITCHER_TIMEFIELDS:
                if v in self.data.keys():
                    if self.data[v]:
                        self.data[v] = cast_utc_time(self.data[v])
            if all([v in self.data.keys() for v in constants.STITCHER_FORM_REQUIRED_KEYS]):
                disable_stitching = False if self.data[constants.STITCHER_APPROVED] is None else True
                disable_delete = True if self.data[constants.STITCHER_APPROVED] else False
                potential_samples = self.get_potential_samples(self.data)
            first_potential_sample = potential_samples[0][0] if potential_samples else None
            if ((self.data[constants.STITCHER_ANNOTATIONS_SEGMENT]
                    or self.data[constants.STITCHER_ANNOTATIONS_UPDATED_AT_SEGMENT])
                    and self.data[constants.STITCHER_APPROVED]
                    and self.data[constants.STITCHER_BUGBOX_SAMPLE_ID]):
                disable_crop_save = False
        context.update({
            'data': self.data,
            'task_response': self.task_response,
            'panoarma_name': self.panorama_name,
            'img_src': f'{self.stitcher_js_url}{self.img_src}',
            'thumbnail_src': f'{self.stitcher_js_url}{self.thumbnail_src}',
            'label_src': f'{self.stitcher_js_url}{self.label_src}',
            'potential_samples': potential_samples,
            'nota_sample': self.nota_sample,
            'first_potential_sample': first_potential_sample,
            'form_action_url': reverse(
                'core:stitcher-form', kwargs={'guid': str(self.guid)}),
            'form_iden_crop_save': constants.STITCHER_FORM_CROPSAVE,
            'form_iden_default': constants.STITCHER_FORM_DEFAULT,
            'form_iden_post_cropped': constants.STITCHER_FORM_POST_CROPPED,
            'disable_crop_save': disable_crop_save,
            'json_context': get_json_context({
                constants.STITCHER_GUID: self.guid,
                'STITCHER_URL': self.stitcher_js_url,
                'disable_stitching': disable_stitching,
                'disable_delete': disable_delete,
                'stitcher_delete_url': reverse(
                    'core:stitcher-delete', kwargs={constants.STITCHER_GUID: str(self.guid)}),
                'first_potential_sample': first_potential_sample,
                'panorama_confidence': self.data.get(constants.STITCHER_PANORAMA_CONFIDENCE),
                'panorama_timestamp': self.data.get(constants.STITCHER_PANORAMA_TIMESTAMP),
                'panorama_path': self.data.get(constants.STITCHER_PANORAMA_PATH),
                'panorama_status_url': reverse(
                    'core:stitcher-panorama-status', kwargs={constants.STITCHER_GUID: str(self.guid)})
            })
        })
        if ERROR_MSG_KEY in self.data.keys():
            messages.error(self.request, self.data[ERROR_MSG_KEY])
        return context

    def get_initial(self):
        initial = super().get_initial()
        data = get_upload_file(self.kwargs[constants.STITCHER_GUID])
        if constants.STITCHER_UPLOADFILE_KEY in data.keys():
            uploadfile_data = data[constants.STITCHER_UPLOADFILE_KEY]
            initial[constants.STITCHER_APPROVED] = uploadfile_data[constants.STITCHER_APPROVED]
            initial[constants.STITCHER_UPLOAD_DIR_NAME] = uploadfile_data[constants.STITCHER_UPLOAD_DIR_NAME]
            if not uploadfile_data[constants.STITCHER_BUGBOX_SAMPLE_ID] and not uploadfile_data[constants.STITCHER_NOTA_SAMPLE]:
                potential_samples = self.get_potential_samples(uploadfile_data, strict=True)
                if len(potential_samples) == 1:
                    initial[constants.STITCHER_BUGBOX_SAMPLE_ID] = potential_samples[0][0]
            else:
                initial[constants.STITCHER_BUGBOX_SAMPLE_ID] = uploadfile_data[constants.STITCHER_BUGBOX_SAMPLE_ID]
            initial[constants.STITCHER_NOTA_SAMPLE] = uploadfile_data[constants.STITCHER_NOTA_SAMPLE]
            initial[constants.STITCHER_OMIT_FROM_TRAINING] = uploadfile_data[constants.STITCHER_OMIT_FROM_TRAINING]
        return initial

    def form_valid(self, form):
        formdata = form.cleaned_data
        if formdata[constants.STITCHER_FORM_IDENT] == constants.STITCHER_FORM_DEFAULT:
            # coerece STITCHER_APPROVED dropdown strings to null boolean
            if formdata[constants.STITCHER_APPROVED] == '':
                formdata[constants.STITCHER_APPROVED] = None
            elif formdata[constants.STITCHER_APPROVED] == 'True':
                formdata[constants.STITCHER_APPROVED] = True
            elif formdata[constants.STITCHER_APPROVED] == 'False':
                formdata[constants.STITCHER_APPROVED] = False

            # Check if sample is marked as Retake
            if formdata[constants.STITCHER_APPROVED] is False:
                upload_dir_name = formdata.get(constants.STITCHER_UPLOAD_DIR_NAME)
                if upload_dir_name:
                    # Call Shimsy API - BLOCKS if fails
                    result = create_rescan_request(upload_dir_name)
                    if not result['success']:
                        messages.error(
                            self.request,
                            f'Failed to create rescan request in Shimsy: {result["message"]}. '
                            f'Retake status for this sample in Stitcher has not been saved. '
                            f'Please make sure Shimsy is up and try again.'
                        )
                        form.add_error(constants.STITCHER_APPROVED, "Approved/Retake status was not saved.")
                        return self.form_invalid(form)
                    else:
                        messages.success(
                            self.request,
                            f'Successfully created rescan request in Shimsy: {result["message"]}'
                        )

            # will only proceed with update if Shimsy API succeeded
            v = patch_upload_file(self.guid, formdata)
            if constants.STITCHER_ERROR in v.keys():
                messages.error(
                    self.request, f'{v[constants.STITCHER_ERROR]}'
                )
            else:
                # If sample was approved, cleanup matching retake records
                if formdata[constants.STITCHER_APPROVED] is True:
                    upload_dir_name = formdata.get(constants.STITCHER_UPLOAD_DIR_NAME)
                    if upload_dir_name:
                        cleanup_result = cleanup_matching_retake_records(
                            upload_dir_name,
                            self.guid
                        )

                        if cleanup_result['deleted_count'] > 0:
                            deleted_list = ', '.join(cleanup_result['deleted_samples'][:5])
                            if len(cleanup_result['deleted_samples']) > 5:
                                deleted_list += f' and {len(cleanup_result["deleted_samples"]) - 5} more'

                            messages.success(
                                self.request,
                                f'Successfully updated {self.guid}. '
                                f'Removed {cleanup_result["deleted_count"]} matching retake record(s): {deleted_list}'
                            )
                        # Log errors
                        if cleanup_result['errors']:
                            for error in cleanup_result['errors']:
                                messages.warning(
                                    self.request,
                                    f'Failed to remove retake record {error["sample"]}: {error["error"]}'
                                )
                messages.success(
                    self.request, f'Successfully updated {self.guid}'
                )
        elif formdata[constants.STITCHER_FORM_IDENT] == constants.STITCHER_FORM_POST_CROPPED:
            # limit what data is updated in STITCHER_FORM_POST_CROPPED by dict update
            limited_formdata = {key: item for key, item in self.data.items() if key in formdata.keys()}
            limited_formdata.update({
                constants.STITCHER_OMIT_FROM_TRAINING: formdata[constants.STITCHER_OMIT_FROM_TRAINING]
            })
            v = patch_upload_file(self.guid, limited_formdata)
            messages.success(
                self.request, f'Successfully updated {self.guid}'
            )
        elif formdata[constants.STITCHER_FORM_IDENT] == constants.STITCHER_FORM_CROPSAVE:
            try:
                this_sample = Sample.objects.user_access(self.request.user).get(
                    id=self.data[constants.STITCHER_BUGBOX_SAMPLE_ID])
            except Exception:
                raise Http404
            try:
                label_url = f'{self.stitcher_url}{self.label_src}'
                label_response = requests.get(label_url, stream=True, timeout=25)
                label_response.raise_for_status()
            except Exception:
                label_response = None
            try:
                img_url = f'{self.stitcher_url}{self.img_src}'
                response = requests.get(img_url, stream=True, timeout=25)
                response.raise_for_status()
                predictions_timestamp = cast_utc_time(self.data[constants.STITCHER_PREDICTIONS_TIMESTAMP_COCO])
                auat = self.data[constants.STITCHER_ANNOTATIONS_UPDATED_AT_SEGMENT]
                instance = MultiSpecimenImage(
                    sample=this_sample,
                    panorama_filename=self.panorama_name,
                    annotations_segment=self.data[constants.STITCHER_ANNOTATIONS_SEGMENT],
                    annotations_updated_at_segment=auat if auat else '',
                    predictions_coco=self.data[constants.STITCHER_PREDICTIONS_COCO],
                    predictions_timestamp_coco=predictions_timestamp,
                    upload_dir_name=self.data[constants.STITCHER_UPLOAD_DIR_NAME],
                    uuid=self.data[constants.STITCHER_GUID],
                    uploaded_by_user=self.request.user)
                img_name = f'{self.data[constants.STITCHER_UPLOAD_DIR_NAME]}.jpg'
                instance.image.save(img_name, ContentFile(response.content), save=False)
                if self.thumbnail_src:
                    thumbnail_url = f'{self.stitcher_url}{self.thumbnail_src}'
                    thumb_response = requests.get(thumbnail_url, stream=True, timeout=25)
                    thumb_response.raise_for_status()
                    thumb_name = f'{self.data[constants.STITCHER_UPLOAD_DIR_NAME]}_thumbnail.jpg'
                    instance.image_thumbnail.save(thumb_name, ContentFile(thumb_response.content), save=False)
                if label_response:
                    label_img_name = f'{self.data[constants.STITCHER_UPLOAD_DIR_NAME]}_label.jpg'
                    instance.label_image.save(label_img_name, ContentFile(label_response.content), save=False)
                    # Save label image to Sample image field
                    if not this_sample.image:
                        sample_label_img_name = f'{self.data[constants.STITCHER_UPLOAD_DIR_NAME]}_label.jpg'
                        this_sample.image.save(
                            sample_label_img_name, ContentFile(label_response.content), save=False)
                        this_sample.save()
                instance.save()
                transaction.on_commit(
                    lambda: crop_panorama_segmentation.delay((instance.id,), this_sample.id, self.request.user.id)
                )
                messages.success(
                    self.request, f'Succesfully initiated "Save to sample and crop" for {self.guid}')
                self.data[constants.STITCHER_BUGBOX_CROPED_SAVED] = str(instance.id)
                patch_upload_file(self.guid, self.data)
            except IntegrityError as e:
                messages.error(self.request, f'Error, possible duplicate image for this record, {e}')
            except Exception as e:
                messages.error(self.request, f'There was an error in "Save to sample". {e}')
        else:
            messages.error(self.request, 'There was an error in form submission.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('core:stitcher-form', kwargs={constants.STITCHER_GUID: self.guid})

    def get_potential_samples(self, data, strict=False):
        dir_name = data[constants.STITCHER_UPLOAD_DIR_NAME]
        vs = dir_name.split('_')
        if strict and len(vs) < 3:
            return []
        if vs:
            samples_w_type = None
            samples_w_transect = None
            sample_ids = []
            samples = Sample.objects.user_access(self.request.user).filter(
                site_visit__site__site_name__icontains=vs[0]
            )
            if len(vs) >= 2:
                if vs[1].lower() in STITCHER_SAMPLE_TYPES.keys():
                    sample_type = STITCHER_SAMPLE_TYPES[vs[1].lower()]
                    samples_w_type = samples.filter(sample_type=sample_type)
                if len(vs) >= 3 and samples_w_type:
                    samples_w_transect = samples_w_type.filter(name_no__icontains=vs[2])
                    if strict:
                        sample_ids = samples_w_transect.values_list('id', flat=True)
                        return [(i, reverse('samples:sample', kwargs={'sample_id': i})) for i in sample_ids]
            if samples_w_transect:
                sample_ids = samples_w_transect.values_list('id', flat=True)
            elif samples_w_type:
                sample_ids = samples_w_type.values_list('id', flat=True)
            else:
                sample_ids = samples.values_list('id', flat=True)
            return [(i, reverse('samples:sample', kwargs={'sample_id': i})) for i in sample_ids]
        else:
            return []


class StitcherDeleteView(PermissionRequiredMixin, FormView):

    permission_required = IS_ADMIN

    form_class = StitcherDeleteForm
    template_name = 'core/confirm_delete_cris.html'

    def get_context_data(self, **kwargs):
        context = super(StitcherDeleteView, self).get_context_data(**kwargs)
        orgs = OrganizationUser.objects.filter(
            user=self.request.user).values_list(
                'organization_id', flat=True)
        if not orgs:
            raise Http404
        information = 'Are you sure you want to delete Shimsy upload with guid {0}'.format(
            self.kwargs[constants.STITCHER_GUID]
        )
        context.update({
            'information': information
        })
        return context

    def get_initial(self):
        initial = super().get_initial()
        guid = self.kwargs[constants.STITCHER_GUID]
        data = get_upload_file(guid)
        if constants.STITCHER_UPLOADFILE_KEY not in data.keys():
            raise Http404
        self.upload_dir_name = data[constants.STITCHER_UPLOADFILE_KEY][constants.STITCHER_UPLOAD_DIR_NAME]
        initial[constants.STITCHER_UPLOAD_DIR_NAME] = self.upload_dir_name
        initial[constants.STITCHER_GUID] = guid
        return initial

    def form_valid(self, form):
        data = form.cleaned_data
        response = delete_upload_file(data['guid'])
        if ERROR_MSG_KEY in response.keys():
            messages.error(self.request, response[ERROR_MSG_KEY])
        else:
            messages.warning(
                    self.request,
                    f'Succesfully deleted {self.upload_dir_name}'
                )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('core:stitcher')


class StitcherPanoramaStatusView(PermissionRequiredMixin, View):
    """Returns JSON with current panorama_timestamp and panorama_path for a guid (for polling after update stitching)"""
    permission_required = IS_ADMIN

    def get(self, request, *args, **kwargs):
        guid = self.kwargs[constants.STITCHER_GUID]
        data = get_upload_file(guid)
        if ERROR_MSG_KEY in data:
            return JsonResponse({ERROR_MSG_KEY: str(data[ERROR_MSG_KEY])}, status=400)
        uploadfile = data.get(constants.STITCHER_UPLOADFILE_KEY, data)
        return JsonResponse({
            'panorama_timestamp': uploadfile.get(constants.STITCHER_PANORAMA_TIMESTAMP),
            'panorama_path': uploadfile.get(constants.STITCHER_PANORAMA_PATH),
        })
