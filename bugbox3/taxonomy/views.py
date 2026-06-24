import csv
import time
from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.files.storage import default_storage
from django.db.models import Count, Q
from django.http import Http404, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import CreateView, FormView, TemplateView, UpdateView
from organizations.models import OrganizationUser
from rest_framework.reverse import reverse as api_reverse
from rest_framework.viewsets import ReadOnlyModelViewSet

from ..core.models import Exports, LookupChoices
from ..core.permissions import (
    ADD_MORPHOSPECIES,
    CHANGE_MORPHOSPECIES,
    IS_RESEARCH,
    user_has_morphospecies_research_or_reviewer_access,
    user_has_specimen_reviewer_access,
    user_in_taxonomy_reviewer_group,
    user_is_taxonomy_only_reviewer,
)
from ..core.views import DatatablesModelViewSetMixin
from ..libs.ui_helpers import calc_image_height, get_datatables_container, get_datatables_row
from ..libs.utilities import get_json_context, get_media_url
from ..samples import constants as samples_constants
from ..samples.models import Sample, Specimen, SpecimenImage
from . import constants
from .constants import (
    EXPORT_TITLE_TRAINING_SELECTIONS,
    FIELD_MORPHO_TAXONOMY_REVIEWED,
)
from .functional_groups import build_grouped_trait_display, get_trait_weights_for_morphospecies
from .forms import MorphospeciesCombineForm, MorphospeciesForm, MorphospeciesUpdateForm
from .mixins import MorphospeciesResearchOrReviewerMixin
from .models import AiTraining, Morphospecies
from .serializers import MorphospeciesDatatablesSerializer, MorphospeciesPickerSerializer
from .tasks import id_image
from .utils import morphospecies_taxonomy_fields_changed


def _morphospecies_queryset_names_with_digit(qs):
    """Restrict to morphospecies whose `name` contains at least one digit (for example 'Acaridae 001')."""
    digit_q = Q()
    for d in '0123456789':
        digit_q |= Q(**{f'{constants.FIELD_MORPHO_NAME}__contains': d})
    return qs.filter(digit_q)


class MorphospeciesDatatablesViewSet(
    MorphospeciesResearchOrReviewerMixin,
    DatatablesModelViewSetMixin,
    ReadOnlyModelViewSet,
):
    serializer_class = MorphospeciesDatatablesSerializer
    search_vector = (
        constants.FIELD_MORPHO_NAME,
        constants.FIELD_MORPHO_GBIF_CANONICAL_NAME
    )

    def get_queryset(self):
        gbif_rank = None
        first_check = None
        tags_filter = None
        morphospecies = Morphospecies.objects.all()
        if self.request.query_params.get('first_filter'):
            gbif_rank = self.request.query_params.get('first_filter')
        if self.request.query_params.get('first_check'):
            first_check = self.request.query_params.get('first_check')
        if self.request.query_params.get('tags_filter'):
            tags_filter = self.request.query_params.get('tags_filter')
        if gbif_rank in constants.GBIF_RANK_VALUES:
            morphospecies = morphospecies.filter(gbif_rank=gbif_rank)
        if tags_filter:
            morphospecies = morphospecies.filter(tags__contains=[tags_filter])
        if not first_check:
            morphospecies = morphospecies.exclude(defunt_date__isnull=False)
        if (
            self.request.query_params.get('hide_reviewed')
            and user_in_taxonomy_reviewer_group(self.request.user)
        ):
            morphospecies = morphospecies.exclude(
                Q(taxonomy_reviewed=True) | Q(taxonomy_identified=True)
            )
        if user_is_taxonomy_only_reviewer(self.request.user):
            morphospecies = _morphospecies_queryset_names_with_digit(morphospecies)
        return morphospecies.order_by(constants.FIELD_MORPHO_NAME)


class MorphospeciesPickerViewSet(
    MorphospeciesResearchOrReviewerMixin,
    DatatablesModelViewSetMixin,
    ReadOnlyModelViewSet,
):
    serializer_class = MorphospeciesPickerSerializer
    search_vector = (
        constants.FIELD_MORPHO_NAME,
        constants.FIELD_MORPHO_GBIF_CANONICAL_NAME
    )

    def get_queryset(self):
        morphospecies = Morphospecies.objects.filter(defunt_date__isnull=True)
        if self.request.query_params.get('first_filter'):
            gbif_rank = self.request.query_params.get('first_filter')
            if gbif_rank in constants.GBIF_RANK_VALUES:
                return morphospecies.filter(gbif_rank=gbif_rank).order_by(constants.FIELD_MORPHO_NAME)
        return morphospecies.order_by(constants.FIELD_MORPHO_NAME)

    def test_func(self):
        user = self.request.user
        return user_has_morphospecies_research_or_reviewer_access(user) or user_has_specimen_reviewer_access(user)


class MophospeciesView(MorphospeciesResearchOrReviewerMixin, TemplateView):
    template_name = 'taxonomy/morphospecies.html'

    first_check_txt = 'Show defunct morphospecies'

    def get_morphospecies_datatable(self, datatables_url, *, show_taxonomy_review_filter):
        """
        Forat the datatables context, including the url from rest_framework.reverse
        as datatables_url
        """
        org_user = OrganizationUser.objects.filter(user=self.request.user).first()
        tags_choices = []
        if org_user:
            tags_choices = LookupChoices.objects.get_field_choices(
                org_user.organization_id, constants.FIELD_MORPHO_TAGS_LOOKUP)
        return {
            'json_context': get_json_context({
                'datatables_url': datatables_url,
                'first_picker_choices': constants.GBIF_RANK_CHOICES_WO_BLANK_LIST,
                'first_picker_text': 'any rank',
                'first_check': self.first_check_txt,
                'tags_picker_choices': tags_choices,
                'tags_picker_text': 'any tag',
                'show_taxonomy_review_filter': show_taxonomy_review_filter,
            }),
            'container_row_header': get_datatables_container(
                get_datatables_row([
                    'Name',
                    'Canonical Name',
                    'Rank'
                ])),
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        training_selections_download = Exports.objects.filter(
            organization_id=samples_constants.PRIMARY_ORGANIZATION_ID,
            title=EXPORT_TITLE_TRAINING_SELECTIONS
        ).order_by('date_added').last()
        if training_selections_download:
            training_selections_download = get_media_url(training_selections_download.file)
        datatables_url = api_reverse('taxonomy:morphospecies-data-list',
                                     kwargs=kwargs)
        show_taxonomy_review_filter = user_in_taxonomy_reviewer_group(self.request.user)
        context.update(self.get_morphospecies_datatable(
            datatables_url, show_taxonomy_review_filter=show_taxonomy_review_filter))
        context.update({
            'can_add': self.request.user.has_perm(ADD_MORPHOSPECIES),
            'exp_morph_choices': constants.EXP_MORPH_CHOICES,
            'first_check': self.first_check_txt,
            'training_selections_download': training_selections_download,
            'can_show_morphospecies_export': not user_is_taxonomy_only_reviewer(self.request.user),
        })
        return context


class MorphospeciesDetailView(MorphospeciesResearchOrReviewerMixin, FormView):

    form_class = MorphospeciesCombineForm
    template_name = 'taxonomy/morphospecies_detail.html'

    def post(self, request, *args, **kwargs):
        if request.POST.get('taxonomy_reviewed_form'):
            if not user_in_taxonomy_reviewer_group(request.user):
                return HttpResponseForbidden()
            if not request.user.has_perm(CHANGE_MORPHOSPECIES):
                return HttpResponseForbidden()
            morphospecies = get_object_or_404(Morphospecies, id=self.kwargs['id'])
            morphospecies.taxonomy_reviewed = (
                request.POST.get(FIELD_MORPHO_TAXONOMY_REVIEWED) == 'on'
            )
            morphospecies.taxonomy_reviewed_by = request.user
            morphospecies.taxonomy_reviewed_at = timezone.now()
            morphospecies.save(
                update_fields=[
                    'taxonomy_reviewed',
                    'taxonomy_reviewed_by',
                    'taxonomy_reviewed_at',
                ]
            )
            messages.success(request, 'Reviewed status saved.')
            return redirect('taxonomy:morphospecies-detail', id=morphospecies.id)
        return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        morphospecies = get_object_or_404(Morphospecies, id=self.kwargs['id'])
        image_set = []
        if morphospecies.gbif_rank == constants.GBIF_RANK_SPECIES and morphospecies.gbif_canonical_name:
            display_name = morphospecies.gbif_canonical_name
        else:
            display_name = morphospecies.name
        image_count = SpecimenImage.objects.filter(
            specimen__classification=morphospecies,
            specimen__sample__site_visit__site__experiment__organization_id=samples_constants.
            PRIMARY_ORGANIZATION_ID).count()
        if image_count:
            archive = 'specimen__' + samples_constants.FIELD_SPECIMEN_ARCHIVAL_IDENTIFIER
            s_images = SpecimenImage.objects.filter(
                specimen__classification=morphospecies,
                specimen__sample__site_visit__site__experiment__organization_id=samples_constants.
                PRIMARY_ORGANIZATION_ID).order_by(
                archive, samples_constants.SPECIMEN_IMAGE_PRIMARY)[:5]
            for s in s_images:
                if s.image_thumbnail_medium:
                    i = s.image_thumbnail_medium
                else:
                    i = s.image
                specimen_link = reverse('samples:specimen', kwargs={'id': s.specimen_id})
                local_info = [
                    s.specimen.sample.site_visit.visit_date.strftime("%d-%b-%Y"),
                    s.specimen.sample.site_visit.site.state_region,
                    s.specimen.sample.site_visit.site.county_region
                ]
                image_set.append({
                    'path': get_media_url(i, s.public_image),
                    'local_info': ' | '.join([v for v in local_info if v]),
                    'specimen_link': specimen_link
                })
        img_thumbnail = None
        img = None
        if morphospecies.image_thumbnail:
            if default_storage.exists(morphospecies.image_thumbnail.name):
                img_thumbnail = {
                    'path': get_media_url(morphospecies.image_thumbnail),
                    'height': morphospecies.image_thumbnail.height,
                    'width': morphospecies.image_thumbnail.width
                }
        elif morphospecies.image:
            if default_storage.exists(morphospecies.image.name):
                img_thumbnail = {
                    'path': get_media_url(morphospecies.image),
                    'height': calc_image_height(
                        constants.MORPHPOSPECIES_THUMBSIZE,
                        morphospecies.image.height,
                        morphospecies.image.width
                    ),
                    'width': constants.MORPHPOSPECIES_THUMBSIZE
                }
        if morphospecies.image:
            if default_storage.exists(morphospecies.image.name):
                img = {
                    'path': get_media_url(morphospecies.image),
                    'height': morphospecies.image.height,
                    'width': morphospecies.image.width
                }
        ai = AiTraining.objects.filter(morphospecies=morphospecies).order_by('id').all()
        ai_accuracy_over_time = {
            'precision': [[a.entered_date, a.precision] for a in ai],
            'f1': [[a.entered_date, a.f1] for a in ai],
            'recall': [[a.entered_date, a.recall] for a in ai],
            'total': [a.train for a in ai]
        }

        reviewed_specimens = Specimen.objects.filter(
            classification=morphospecies
        ).exclude(acceptance=samples_constants.ACCEPTANCE_PENDING)

        misidentification_counts = {}
        for specimen in reviewed_specimens:
            # Check top-3: ai_classification, optional_pred_one, optional_pred_two
            top3_morphospecies = []

            if specimen.ai_classification and specimen.ai_classification.id != morphospecies.id:
                top3_morphospecies.append(specimen.ai_classification)

            # Secondary prediction
            if specimen.optional_pred_one:
                pred_one_morpho = None
                if 'morphospecies_id' in specimen.optional_pred_one:
                    try:
                        pred_one_morpho = Morphospecies.objects.get(pk=specimen.optional_pred_one['morphospecies_id'])
                    except (Morphospecies.DoesNotExist, ValueError, TypeError):
                        pass
                elif 'class_op' in specimen.optional_pred_one:
                    pred_one_name = specimen.optional_pred_one.get('class_op')
                    if pred_one_name:
                        try:
                            pred_one_morpho = Morphospecies.objects.get(name=pred_one_name)
                        except Morphospecies.DoesNotExist:
                            pass
                if pred_one_morpho and pred_one_morpho.id != morphospecies.id:
                    top3_morphospecies.append(pred_one_morpho)

            # Tertiary prediction
            if specimen.optional_pred_two:
                pred_two_morpho = None
                if 'morphospecies_id' in specimen.optional_pred_two:
                    try:
                        pred_two_morpho = Morphospecies.objects.get(pk=specimen.optional_pred_two['morphospecies_id'])
                    except (Morphospecies.DoesNotExist, ValueError, TypeError):
                        pass
                elif 'class_op' in specimen.optional_pred_two:
                    pred_two_name = specimen.optional_pred_two.get('class_op')
                    if pred_two_name:
                        try:
                            pred_two_morpho = Morphospecies.objects.get(name=pred_two_name)
                        except Morphospecies.DoesNotExist:
                            pass
                if pred_two_morpho and pred_two_morpho.id != morphospecies.id:
                    top3_morphospecies.append(pred_two_morpho)

            # count the occurrences
            for misidentified_morpho in top3_morphospecies:
                if misidentified_morpho.id not in misidentification_counts:
                    misidentification_counts[misidentified_morpho.id] = {
                        'morphospecies': misidentified_morpho,
                        'count': 0
                    }
                misidentification_counts[misidentified_morpho.id]['count'] += 1

        #  sort by count and geting the top results -descending-
        common_misidentifications = sorted(
            misidentification_counts.values(),
            key=lambda x: x['count'],
            reverse=True
        )

        user = self.request.user
        trait_weights = get_trait_weights_for_morphospecies(morphospecies)
        context.update({
            'can_edit_taxonomy': user.has_perm(CHANGE_MORPHOSPECIES),
            'show_taxonomy_reviewer_reviewed': user_in_taxonomy_reviewer_group(user),
            'can_combine': user.has_perms(IS_RESEARCH) and user.has_perm(CHANGE_MORPHOSPECIES),
            'display_name': display_name,
            'morphospecies': morphospecies,
            'functional_group_sections': build_grouped_trait_display(trait_weights),
            'ai_last_train': ai_accuracy_over_time['total'][-1] if ai_accuracy_over_time['total'] else 0,
            'image_set': image_set,
            'image_count': image_count,
            'img_thumbnail': img_thumbnail,
            'img': img,
            'specimen_count_reviewed': Specimen.objects.filter(
                classification=morphospecies,
                sample__site_visit__site__experiment__organization_id=samples_constants.PRIMARY_ORGANIZATION_ID,
            ).count(),
            'specimen_count_pending_review': Specimen.objects.filter(
                classification__isnull=True,
                ai_classification=morphospecies,
                sample__site_visit__site__experiment__organization_id=samples_constants.PRIMARY_ORGANIZATION_ID,
            ).count(),
            'common_misidentifications': common_misidentifications,
            'json_context': get_json_context({
                'ai_accuracy_over_time': ai_accuracy_over_time,
                'datatables_url': api_reverse('taxonomy:morphospecies-picker-list', kwargs=kwargs),
                'first_picker_choices': constants.GBIF_RANK_CHOICES_WO_BLANK_LIST,
                'first_picker_text': 'any rank',
            })
        })
        return context

    def form_valid(self, form):
        combine_to_id = form.cleaned_data['combine_to_id']
        if combine_to_id and self.request.user.has_perms(IS_RESEARCH) and self.request.user.has_perm(
                CHANGE_MORPHOSPECIES):
            morphospecies = get_object_or_404(Morphospecies, id=self.kwargs['id'])
            combine_to = get_object_or_404(Morphospecies, id=combine_to_id)

            if morphospecies.id != combine_to.id:
                if not morphospecies.defunt_date:
                    Specimen.objects.filter(classification=morphospecies).update(
                        classification_id=combine_to.id)
                    Specimen.objects.filter(ai_classification=morphospecies).update(
                        ai_classification_id=combine_to.id)
                    morphospecies.defunt_date = datetime.today()
                    morphospecies.defunt_user = self.request.user
                    morphospecies.defunt_morpho = combine_to
                    morphospecies.save()

                    messages.success(self.request, 'Successfully combined {0} (id={1}) to {2} (id={3})'.format(
                        morphospecies.name, morphospecies.id, combine_to.name, combine_to.id))
                else:
                    messages.warning(
                        self.request, 'Warning: {0} (id={3}) is a defunct Morphospecies, did not save changes').format(
                        combine_to.name, combine_to.id
                    )
            else:
                messages.warning(
                    self.request, 'Warning: {0} (id={1}) is the same as {2} (id={3}), did not save changes'.format(
                        morphospecies.name, morphospecies.id, combine_to.name, combine_to.id))
        return super().form_valid(form)

    def get_success_url(self):
        if self.request.POST.get('combine_to_id'):
            return reverse(
                'taxonomy:morphospecies'
            )
        return reverse('taxonomy:morphospecies-detail', kwargs={'id': self.kwargs['id']})


class MorphospeciesCreateView(PermissionRequiredMixin, CreateView):

    permission_required = IS_RESEARCH + [ADD_MORPHOSPECIES]
    form_class = MorphospeciesForm
    template_name = 'taxonomy/morphospecies_form.html'
    action = 'create'

    def get_context_data(self, **kwargs):
        context = super(MorphospeciesCreateView, self).get_context_data(**kwargs)
        context.update({'json_context': get_json_context({
            'action': self.action
        })})
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Successfully created a Morphospecies')
        return super(MorphospeciesCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('taxonomy:morphospecies-detail', kwargs={'id': self.object.id})


class MorphospeciesUpdateView(MorphospeciesResearchOrReviewerMixin, UpdateView):

    form_class = MorphospeciesUpdateForm
    template_name = 'taxonomy/morphospecies_form_update.html'
    action = 'update'

    def test_func(self):
        u = self.request.user
        return u.has_perm(CHANGE_MORPHOSPECIES) and user_has_morphospecies_research_or_reviewer_access(u)

    def get_object(self, queryset=None):
        return get_object_or_404(Morphospecies, id=self.kwargs['id'])

    def get_form_kwargs(self):
        kwargs = super(MorphospeciesUpdateView, self).get_form_kwargs()
        org_user = OrganizationUser.objects.filter(user=self.request.user).first()
        if org_user:
            kwargs['org_id'] = org_user.organization_id
        kwargs['taxonomy_reviewer_user'] = user_in_taxonomy_reviewer_group(self.request.user)
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(MorphospeciesUpdateView, self).get_context_data(**kwargs)
        context.update({'json_context': get_json_context({
            'action': self.action
        })})
        return context

    def form_valid(self, form):
        old = Morphospecies.objects.get(pk=self.object.pk)
        instance = form.instance
        reviewer = user_in_taxonomy_reviewer_group(self.request.user)
        taxonomy_changed = morphospecies_taxonomy_fields_changed(old, instance)
        if taxonomy_changed:
            instance.taxonomy_reviewed = False
            if reviewer:
                instance.taxonomy_identified = True
                instance.taxonomy_reviewed_by = self.request.user
                instance.taxonomy_reviewed_at = timezone.now()
        elif reviewer and form.cleaned_data.get(FIELD_MORPHO_TAXONOMY_REVIEWED) != old.taxonomy_reviewed:
            instance.taxonomy_reviewed_by = self.request.user
            instance.taxonomy_reviewed_at = timezone.now()
        messages.success(self.request, 'Successfully updated a Morphospecies')
        return super(MorphospeciesUpdateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('taxonomy:morphospecies-detail', kwargs={'id': self.object.id})


@permission_required(IS_RESEARCH)
def classify_specimen(request, id):
    if not settings.AI_INFERENCE_URL:
        return Http404('The AI_INFERENCE_URL is not avaialble')
    id_image.delay(id)
    time.sleep(2)
    return redirect(request.META['HTTP_REFERER'])


@permission_required(IS_RESEARCH)
def classify_sample(request, id):
    if not settings.AI_INFERENCE_URL:
        return Http404('The AI_INFERENCE_URL is not avaialble')
    try:
        sample = Sample.objects.user_access(request.user).get(id=id)
    except Sample.DoesNotExist:
        raise Http404
    specimen = Specimen.objects.filter(sample=sample, acceptance=0)
    for s in specimen:
        id_image.delay(s.id)
    time.sleep(3)
    return redirect(request.META['HTTP_REFERER'])


@permission_required(IS_RESEARCH)
def morphospecies_csv(request):
    response = HttpResponse(content_type='text/csv')
    name = request.GET.get('name')
    name = name if name in constants.EXP_MORPH_CHOICES_NAMES else ''
    headers = ['None']
    result_values_list = []

    if name == constants.EXP_MORPH_ALL_MORPH:
        headers = constants.EXPORT_HEADERS_MORPHOSPECIES
        result_values_list = Morphospecies.objects.values_list(*headers)
    timestr = time.strftime("%Y%m%d-%H%M%S")
    response['Content-Disposition'] = 'attachment; filename="{0}-{1}.csv"'.format(
        name, timestr)
    writer = csv.writer(response)
    writer.writerow(headers)
    writer.writerows(list(result_values_list))

    return response
