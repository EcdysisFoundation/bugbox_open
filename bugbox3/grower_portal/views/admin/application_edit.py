from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from bugbox3.core.permissions import IS_GROWERADMIN

from ...constants import DEFAULT_FIELD_LATITUDE, DEFAULT_FIELD_LONGITUDE
from ...forms.grower.forms import ApplicationCreationForm, ManagementPracticesForm, TransectCodesForm
from ...middleware import get_user_timezone
from ...models import (
    Farm,
    Field,
    GrazingEvent,
    GrowerApplication,
    ManagementPractices,
    SampleCode,
    TransectMeasurement,
)
from ...utils import (
    build_interactive_transect_data,
    get_grower_maps_json_context,
    get_grower_maps_json_context_interactive,
)


def _require_draft_for_wizard_edit(request, application):
    if application.is_draft:
        return None
    messages.error(request, 'Only draft applications can be edited through the wizard.')
    return redirect('grower_portal:admin_application_detail', application_id=application.id)


def _require_transect_codes_for_edit_wizard(request, application):
    """Steps 4+ need at least one transect code"""
    if application.transect_codes:
        return None
    messages.error(
        request,
        'Please enter at least one transect code before recording measurements.',
    )
    return redirect('grower_portal:admin_application_edit_transects', application_id=application.id)


@login_required
@permission_required(IS_GROWERADMIN, raise_exception=True)
def admin_application_edit_basic(request, application_id):
    application = get_object_or_404(GrowerApplication, id=application_id)
    block = _require_draft_for_wizard_edit(request, application)
    if block:
        return block

    if request.method == 'POST':
        form = ApplicationCreationForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    if application.grower:
                        farm, created = Farm.objects.get_or_create(
                            grower=application.grower,
                            name=form.cleaned_data['farm_name']
                        )
                    else:
                        farm, created = Farm.objects.get_or_create(
                            grower=None,
                            name=form.cleaned_data['farm_name']
                        )

                    cd = form.cleaned_data
                    if application.field is None:
                        field = Field(
                            farm=farm,
                            field_name=cd['field_name'],
                            field_type=cd['field_type'],
                            acres_sampled=cd.get('acres_sampled'),
                            years_under_management=cd.get('years_under_management'),
                            supports_dairy=cd.get('supports_dairy', False),
                            is_confined_dairy=cd.get('is_confined_dairy', False),
                            measurement_comments=cd.get('measurement_comments', ''),
                            crop_type=cd.get('crop_type', ''),
                            crop_subtype=cd.get('crop_subtype', ''),
                            crop_subtype_other=cd.get('crop_subtype_other', ''),
                            small_grain_type=cd.get('small_grain_type', ''),
                            tillage_methods=cd.get('tillage_methods', ''),
                            orchard_crop_specify=cd.get('orchard_crop_specify', ''),
                            forage_varieties=cd.get('forage_varieties', ''),
                            paddock_size=cd.get('paddock_size', ''),
                            pasture_size=cd.get('pasture_size', ''),
                            rootstock_species=cd.get('rootstock_species', ''),
                            crop_varieties=cd.get('crop_varieties', ''),
                            transitional_status=cd.get('transitional_status', ''),
                        )
                        if cd.get('orchard_crop_type'):
                            field.crop_type = cd.get('orchard_crop_type', '')
                        field.save()
                        application.field = field
                    else:
                        field = application.field
                        field.farm = farm
                        field.field_name = cd['field_name']
                        field.field_type = cd['field_type']
                        field.acres_sampled = cd.get('acres_sampled')
                        field.years_under_management = cd.get('years_under_management')
                        field.supports_dairy = cd.get('supports_dairy', False)
                        field.is_confined_dairy = cd.get('is_confined_dairy', False)
                        field.measurement_comments = cd.get('measurement_comments', '')

                        field.crop_type = cd.get('crop_type', '')
                        field.crop_subtype = cd.get('crop_subtype', '')
                        field.crop_subtype_other = cd.get('crop_subtype_other', '')
                        field.small_grain_type = cd.get('small_grain_type', '')
                        field.tillage_methods = cd.get('tillage_methods', '')

                        if cd.get('orchard_crop_type'):
                            field.crop_type = cd.get('orchard_crop_type', '')
                        field.orchard_crop_specify = cd.get('orchard_crop_specify', '')

                        field.forage_varieties = cd.get('forage_varieties', '')
                        field.paddock_size = cd.get('paddock_size', '')
                        field.pasture_size = cd.get('pasture_size', '')

                        field.rootstock_species = cd.get('rootstock_species', '')
                        field.crop_varieties = cd.get('crop_varieties', '')
                        field.transitional_status = cd.get('transitional_status', '')

                        field.save()

                    application.date_sampled = cd['date_sampled']
                    application.save()

                    messages.success(
                        request, f'Application {
                            application.submission_code} basic info updated successfully!')
                    return redirect('grower_portal:admin_application_edit_management', application_id=application.id)

            except Exception as e:
                messages.error(request, f'Error updating application: {str(e)}')
    else:
        if application.field:
            f = application.field
            initial = {
                'farm_name': f.farm.name if f.farm else '',
                'field_name': f.field_name,
                'field_type': f.field_type,
                'date_sampled': application.date_sampled,
                'acres_sampled': f.acres_sampled,
                'years_under_management': f.years_under_management,
                'supports_dairy': f.supports_dairy,
                'is_confined_dairy': f.is_confined_dairy,
                'measurement_comments': f.measurement_comments,
                'crop_type': f.crop_type,
                'crop_subtype': f.crop_subtype,
                'crop_subtype_other': f.crop_subtype_other,
                'small_grain_type': f.small_grain_type,
                'tillage_methods': f.tillage_methods,
                'forage_varieties': f.forage_varieties,
                'paddock_size': f.paddock_size,
                'pasture_size': f.pasture_size,
                'rootstock_species': f.rootstock_species,
                'crop_varieties': f.crop_varieties,
                'transitional_status': f.transitional_status,
                'orchard_crop_type': f.crop_type,
                'orchard_crop_specify': f.orchard_crop_specify,
            }
        else:
            initial = {
                'farm_name': '',
                'field_name': '',
                'field_type': '',
                'date_sampled': application.date_sampled,
                'acres_sampled': None,
                'years_under_management': None,
                'supports_dairy': False,
                'is_confined_dairy': False,
                'measurement_comments': '',
                'crop_type': '',
                'crop_subtype': '',
                'crop_subtype_other': '',
                'small_grain_type': '',
                'tillage_methods': '',
                'forage_varieties': '',
                'paddock_size': '',
                'pasture_size': '',
                'rootstock_species': '',
                'crop_varieties': '',
                'transitional_status': '',
                'orchard_crop_type': '',
                'orchard_crop_specify': '',
            }
        form = ApplicationCreationForm(initial=initial)

    context = {
        'application': application,
        'form': form,
        'user_timezone': get_user_timezone(request),
        'is_admin_edit': True,
        'wizard_step': 'basic',
    }

    return render(request, 'grower_portal/admin/application_edit_basic.html', context)


@login_required
@permission_required(IS_GROWERADMIN, raise_exception=True)
def admin_application_edit_management(request, application_id):
    application = get_object_or_404(GrowerApplication, id=application_id)
    block = _require_draft_for_wizard_edit(request, application)
    if block:
        return block

    practices, created = ManagementPractices.objects.get_or_create(
        application=application
    )

    if request.method == 'POST':
        form = ManagementPracticesForm(request.POST, instance=practices)
        if form.is_valid():
            form.save()
            messages.success(request, 'Management practices updated successfully!')
            return redirect('grower_portal:admin_application_edit_transects', application_id=application.id)
    else:
        form = ManagementPracticesForm(instance=practices)

    context = {
        'application': application,
        'form': form,
        'user_timezone': get_user_timezone(request),
        'is_admin_edit': True,
        'wizard_step': 'management',
    }

    return render(request, 'grower_portal/admin/application_edit_management.html', context)


@login_required
@permission_required(IS_GROWERADMIN, raise_exception=True)
def admin_application_edit_transects(request, application_id):
    application = get_object_or_404(GrowerApplication, id=application_id)
    block = _require_draft_for_wizard_edit(request, application)
    if block:
        return block

    if request.method == 'POST':
        form = TransectCodesForm(
            request.POST,
            field_type=application.field.field_type,
            for_application=application,
        )
        if form.is_valid():
            application.transect_code_1 = form.cleaned_data.get('transect_code_1', '').strip()
            application.transect_code_2 = form.cleaned_data.get('transect_code_2', '').strip()
            application.transect_code_3 = form.cleaned_data.get('transect_code_3', '').strip()
            application.transect_code_4 = form.cleaned_data.get('transect_code_4', '').strip()

            for i in range(1, 5):
                lat = form.cleaned_data.get(f'transect_{i}_latitude')
                lng = form.cleaned_data.get(f'transect_{i}_longitude')
                application.set_transect_location(i, lng, lat)

            application.save()
            messages.success(request, 'Transect codes updated successfully!')
            return redirect('grower_portal:admin_application_edit_measurements', application_id=application.id)
    else:
        initial_data = {
            'transect_code_1': application.transect_code_1 or '',
            'transect_code_2': application.transect_code_2 or '',
            'transect_code_3': application.transect_code_3 or '',
            'transect_code_4': application.transect_code_4 or '',
        }
        for i in range(1, 5):
            location = getattr(application, f'transect_{i}_location', None)
            if location:
                initial_data[f'transect_{i}_latitude'] = location.y
                initial_data[f'transect_{i}_longitude'] = location.x
            else:
                initial_data[f'transect_{i}_latitude'] = None
                initial_data[f'transect_{i}_longitude'] = None
        form = TransectCodesForm(
            initial=initial_data,
            field_type=application.field.field_type,
            for_application=application,
        )

    field_latitude = DEFAULT_FIELD_LATITUDE
    field_longitude = DEFAULT_FIELD_LONGITUDE

    transect_data = build_interactive_transect_data(
        application, field_latitude, field_longitude,
    )

    context = {
        'application': application,
        'form': form,
        'field_latitude': field_latitude,
        'field_longitude': field_longitude,
        'json_context': get_grower_maps_json_context_interactive(
            transect_data, field_latitude, field_longitude,
        ),
        'user_timezone': get_user_timezone(request),
        'is_admin_edit': True,
        'wizard_step': 'transects',
    }

    return render(request, 'grower_portal/admin/application_edit_transects.html', context)


def _edit_review_page_context(application):
    try:
        management_practices = ManagementPractices.objects.get(application=application)
    except ManagementPractices.DoesNotExist:
        management_practices = None

    grazing_events = GrazingEvent.objects.filter(
        application=application
    ).prefetch_related('animals').order_by('event_number')

    transect_measurements = TransectMeasurement.objects.filter(
        application=application
    ).prefetch_related(
        'drop_plate',
        'vegetation',
        'soil',
        'compaction',
        'infiltrometer',
        'infiltration_ring',
    ).order_by('transect_index')

    map_transect_points = []
    for i, code in enumerate(application.transect_codes):
        location = getattr(application, f'transect_{i + 1}_location', None)
        if location:
            map_transect_points.append({
                'index': i,
                'code': code,
                'latitude': float(location.y),
                'longitude': float(location.x),
            })
    ctx = {
        'management_practices': management_practices,
        'grazing_events': grazing_events,
        'transect_measurements': transect_measurements,
    }
    if application.field:
        ctx['json_context'] = get_grower_maps_json_context(map_transect_points)
    return ctx


@login_required
@permission_required(IS_GROWERADMIN, raise_exception=True)
def admin_application_edit_review(request, application_id):
    application = get_object_or_404(
        GrowerApplication.objects.select_related('grower', 'field', 'field__farm'),
        id=application_id,
    )
    block = _require_draft_for_wizard_edit(request, application)
    if block:
        return block

    block = _require_transect_codes_for_edit_wizard(request, application)
    if block:
        return block

    if request.method == 'POST' and request.POST.get('action') == 'save_draft':
        application.is_draft = True
        application.is_submitted = False
        application.save()
        messages.success(
            request,
            f'Application {application.submission_code} saved as draft.',
        )
        return redirect('grower_portal:admin_application_detail', application_id=application.id)

    ctx = {
        'application': application,
        'user_timezone': get_user_timezone(request),
        'wizard_step': 'review',
        **_edit_review_page_context(application),
    }
    return render(request, 'grower_portal/admin/application_edit_review.html', ctx)


@login_required
@permission_required(IS_GROWERADMIN, raise_exception=True)
def admin_application_submit(request, application_id):
    application = get_object_or_404(GrowerApplication, id=application_id)

    if not application.is_draft:
        messages.error(request, 'This application has already been submitted.')
        return redirect('grower_portal:admin_application_detail', application_id=application.id)

    if request.method == 'POST':
        if not application.transect_code_1:
            messages.error(request, 'Cannot submit: At least one transect code is required.')
            return redirect('grower_portal:admin_application_edit_transects', application_id=application.id)

        # validate transect codes before submission
        for i in range(1, 5):
            code = getattr(
                application,
                f'transect_code_{i}',
                '').strip() if getattr(
                application,
                f'transect_code_{i}',
                None) else ''
            if code:
                try:
                    transect_obj = SampleCode.objects.get(code=code, is_active=True)
                    if transect_obj.is_used and transect_obj.used_in_application != application:
                        submission_code = (
                            transect_obj.used_in_application.submission_code
                            if transect_obj.used_in_application
                            else "another application"
                        )
                        messages.error(
                            request,
                            f'Cannot submit: Transect code {i} "{code}" '
                            f'has already been used in application '
                            f'{submission_code}.'
                        )
                        return redirect(
                            'grower_portal:admin_application_edit_transects',
                            application_id=application.id)
                except SampleCode.DoesNotExist:
                    messages.error(request, f'Cannot submit: Transect code {i} "{code}" is not valid or inactive.')
                    return redirect('grower_portal:admin_application_edit_transects', application_id=application.id)

        if not application.date_sampled:
            messages.error(
                request,
                'Cannot submit: Date sampled is required. Please edit the application '
                'and set the date when samples were collected.'
            )
            return redirect('grower_portal:admin_application_edit_basic', application_id=application.id)
        with transaction.atomic():
            application.is_draft = False
            application.is_submitted = True
            try:
                application.save()
            except ValidationError as e:
                messages.error(request, e.messages[0] if e.messages else str(e))
                return redirect('grower_portal:admin_application_submit', application_id=application.id)
            # mark transect codes as used
            for i in range(1, 5):
                code = getattr(
                    application,
                    f'transect_code_{i}',
                    '').strip() if getattr(
                    application,
                    f'transect_code_{i}',
                    None) else ''
                if code:
                    SampleCode.objects.filter(code=code).update(
                        is_used=True,
                        used_in_application=application,
                        used_at=timezone.now()
                    )

        grower_name = application.grower.name if application.grower and hasattr(
            application.grower, 'name') else application.grower_display_name
        messages.success(
            request,
            f'Application {application.submission_code} has been submitted on behalf of {grower_name}!'
        )
        return redirect('grower_portal:admin_application_detail', application_id=application.id)

    context = {
        'application': application,
        'user_timezone': get_user_timezone(request),
    }

    return render(request, 'grower_portal/admin/application_submit_confirm.html', context)
