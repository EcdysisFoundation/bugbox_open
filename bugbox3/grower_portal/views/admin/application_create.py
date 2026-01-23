import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from bugbox3.core.permissions import IS_GROWERADMIN

from ...forms.admin.application_forms import AdminApplicationCreationForm, GrowerSelectionForm
from ...forms.grower.forms import (
    GrazingEventAnimalFormSet,
    GrazingEventForm,
    ManagementPracticesForm,
    TransectCodesForm,
)
from ...middleware import get_user_timezone
from ...models import Farm, Field, GrazingEvent, GrowerApplication, ManagementPractices, TransectCode


@login_required
@permission_required(IS_GROWERADMIN, raise_exception=True)
def admin_application_create_start(request):
    """Initial page - select grower by email or enter grower info manually"""
    if request.method == 'POST':
        form = GrowerSelectionForm(request.POST)
        if form.is_valid():
            grower_user = form.cleaned_data.get('grower_user')
            grower_name = form.cleaned_data.get('grower_name')
            grower_email_manual = form.cleaned_data.get('grower_email_manual')
            grower_phone = form.cleaned_data.get('grower_phone')

            with transaction.atomic():
                if grower_user:
                    application = GrowerApplication.objects.create(
                        field=None,
                        grower=grower_user,
                        created_by_admin=request.user,
                        is_admin_created=True,
                        is_draft=True
                    )
                    messages.info(request, f'Creating application for {grower_user.email}')
                else:
                    application = GrowerApplication.objects.create(
                        field=None,
                        grower=None,
                        grower_name=grower_name,
                        grower_email=grower_email_manual or '',
                        grower_phone=grower_phone or '',
                        created_by_admin=request.user,
                        is_admin_created=True,
                        is_draft=True
                    )
                    messages.info(request, f'Creating application for {grower_name} (no linked account)')

                return redirect('grower_portal:admin_application_create_step1', application_id=application.id)
    else:
        form = GrowerSelectionForm()

    return render(request, 'grower_portal/admin/application_create/start.html', {
        'form': form,
        'user_timezone': get_user_timezone(request)
    })


@login_required
@permission_required(IS_GROWERADMIN, raise_exception=True)
def admin_application_create_step1(request, application_id):
    """Step 1: Basic information"""
    application = get_object_or_404(
        GrowerApplication,
        id=application_id,
        is_admin_created=True
    )

    if request.method == 'POST':
        post_data = request.POST.copy()
        if 'grower_email' not in post_data or not post_data.get('grower_email'):
            post_data['grower_email'] = application.grower_display_email
        form = AdminApplicationCreationForm(post_data)

        if form.is_valid():
            try:
                with transaction.atomic():
                    # Create or get the farm
                    if application.grower:
                        farm, _ = Farm.objects.get_or_create(
                            grower=application.grower,
                            name=form.cleaned_data['farm_name']
                        )
                    else:
                        farm, _ = Farm.objects.get_or_create(
                            grower=None,
                            name=form.cleaned_data['farm_name']
                        )

                    # Create or get the field
                    existing_field = Field.objects.filter(
                        farm=farm,
                        field_name=form.cleaned_data['field_name']
                    ).first()

                    if existing_field:
                        field = existing_field
                        field.field_type = form.cleaned_data['field_type']
                    else:
                        field = Field.objects.create(
                            farm=farm,
                            field_name=form.cleaned_data['field_name'],
                            field_type=form.cleaned_data['field_type']
                        )

                    application.field = field
                    field.acres_sampled = form.cleaned_data.get('acres_sampled')
                    field.years_under_management = form.cleaned_data.get('years_under_management')
                    field.supports_dairy = form.cleaned_data.get('supports_dairy', False)
                    field.is_confined_dairy = form.cleaned_data.get('is_confined_dairy', False)
                    field.measurement_comments = form.cleaned_data.get('measurement_comments', '')

                    field.crop_type = form.cleaned_data.get('crop_type', '')
                    field.crop_subtype = form.cleaned_data.get('crop_subtype', '')
                    field.crop_subtype_other = form.cleaned_data.get('crop_subtype_other', '')
                    field.small_grain_type = form.cleaned_data.get('small_grain_type', '')
                    field.tillage_methods = form.cleaned_data.get('tillage_methods', '')

                    if form.cleaned_data.get('orchard_crop_type'):
                        field.crop_type = form.cleaned_data.get('orchard_crop_type', '')
                    field.orchard_crop_specify = form.cleaned_data.get('orchard_crop_specify', '')

                    field.forage_varieties = form.cleaned_data.get('forage_varieties', '')
                    field.paddock_size = form.cleaned_data.get('paddock_size', '')
                    field.pasture_size = form.cleaned_data.get('pasture_size', '')

                    field.rootstock_species = form.cleaned_data.get('rootstock_species', '')
                    field.crop_varieties = form.cleaned_data.get('crop_varieties', '')
                    field.transitional_status = form.cleaned_data.get('transitional_status', '')

                    field.save()

                    application.date_sampled = form.cleaned_data['date_sampled']
                    application.save()

                    messages.success(request, f'Application {application.submission_code} - Step 1 completed!')
                    return redirect('grower_portal:admin_application_create_step2', application_id=application.id)

            except IntegrityError as e:
                if 'field_id_date_sampled' in str(e):
                    messages.error(request, f'An application already exists for this field on {
                        form.cleaned_data["date_sampled"].strftime("%B %d, %Y")}.')
                else:
                    messages.error(request, f'Error saving application: {str(e)}')
    else:
        initial_data = {
            'grower_email': application.grower_display_email,
            'farm_name': application.field.farm.name if application.field and application.field.farm else '',
            'field_name': application.field.field_name if application.field else '',
            'field_type': application.field.field_type if application.field else 'crop',
            'date_sampled': application.date_sampled,
            'acres_sampled': application.field.acres_sampled if application.field else None,
            'years_under_management': application.field.years_under_management if application.field else None,
            'supports_dairy': application.field.supports_dairy if application.field else False,
            'is_confined_dairy': application.field.is_confined_dairy if application.field else False,
            'measurement_comments': application.field.measurement_comments if application.field else '',
            'crop_type': (
                application.field.crop_type
                if application.field and application.field.crop_type
                else ''
            ),
            'crop_subtype': (
                application.field.crop_subtype
                if application.field and application.field.crop_subtype
                else ''
            ),
            'crop_subtype_other': (
                application.field.crop_subtype_other
                if application.field and application.field.crop_subtype_other
                else ''
            ),
            'small_grain_type': (
                application.field.small_grain_type
                if application.field and application.field.small_grain_type
                else ''
            ),
            'tillage_methods': (
                application.field.tillage_methods
                if application.field and application.field.tillage_methods
                else ''
            ),
            'forage_varieties': (
                application.field.forage_varieties
                if application.field and application.field.forage_varieties
                else ''
            ),
            'paddock_size': (
                application.field.paddock_size
                if application.field and application.field.paddock_size
                else ''
            ),
            'pasture_size': (
                application.field.pasture_size
                if application.field and application.field.pasture_size
                else ''
            ),
            'rootstock_species': (
                application.field.rootstock_species
                if application.field and application.field.rootstock_species
                else ''
            ),
            'crop_varieties': (
                application.field.crop_varieties
                if application.field and application.field.crop_varieties
                else ''
            ),
            'transitional_status': (
                application.field.transitional_status
                if application.field and application.field.transitional_status
                else ''
            ),
            'orchard_crop_type': (
                application.field.crop_type
                if application.field and application.field.field_type == 'orchard'
                else ''
            ),
            'orchard_crop_specify': (
                application.field.orchard_crop_specify
                if application.field and application.field.orchard_crop_specify
                else ''
            )}
        form = AdminApplicationCreationForm(initial=initial_data)

    return render(request, 'grower_portal/grower/application_step1.html', {
        'application': application,
        'form': form,
        'is_admin': True,
        'grower_display': application.grower_display_name,
        'has_linked_account': application.has_linked_account,
        'user_timezone': get_user_timezone(request)
    })


@login_required
@permission_required(IS_GROWERADMIN, raise_exception=True)
def admin_application_create_step2(request, application_id):
    """Step 2: Management practices"""
    application = get_object_or_404(
        GrowerApplication.objects.select_related('field'),
        id=application_id,
        is_admin_created=True
    )

    if application.field:
        application.field.refresh_from_db()

    practices, _ = ManagementPractices.objects.get_or_create(
        application=application
    )

    is_rangeland = application.field and application.field.field_type == 'range'
    grazing_events = []

    if request.method == 'POST':
        form = ManagementPracticesForm(request.POST, instance=practices)

        if is_rangeland:
            for event_num in range(1, 5):
                event, _ = GrazingEvent.objects.get_or_create(
                    application=application,
                    event_number=event_num
                )
                grazing_form = GrazingEventForm(
                    request.POST,
                    instance=event,
                    prefix=f'grazing_{event_num}'
                )
                grazing_formset = GrazingEventAnimalFormSet(
                    request.POST,
                    instance=event,
                    prefix=f'animals_{event_num}'
                )
                grazing_events.append((event_num, grazing_form, grazing_formset))

        if form.is_valid():
            all_valid = True
            if is_rangeland:
                for _, g_form, g_formset in grazing_events:
                    if not g_form.is_valid() or not g_formset.is_valid():
                        all_valid = False

            if all_valid:
                form.save()

                if is_rangeland:
                    for _, g_form, g_formset in grazing_events:
                        g_form.save()
                        g_formset.save()

                messages.success(request, 'Management practices saved successfully!')
                return redirect('grower_portal:admin_application_create_step3', application_id=application.id)
    else:
        form = ManagementPracticesForm(instance=practices)

        if is_rangeland:
            for event_num in range(1, 5):
                event, _ = GrazingEvent.objects.get_or_create(
                    application=application,
                    event_number=event_num
                )
                grazing_form = GrazingEventForm(
                    instance=event,
                    prefix=f'grazing_{event_num}'
                )
                grazing_formset = GrazingEventAnimalFormSet(
                    instance=event,
                    prefix=f'animals_{event_num}'
                )
                grazing_events.append((event_num, grazing_form, grazing_formset))

    return render(request, 'grower_portal/grower/application_step2.html', {
        'application': application,
        'form': form,
        'is_admin': True,
        'is_rangeland': is_rangeland,
        'grazing_events': grazing_events,
        'grower_display': application.grower_display_name,
        'has_linked_account': application.has_linked_account,
        'user_timezone': get_user_timezone(request)
    })


@login_required
@permission_required(IS_GROWERADMIN, raise_exception=True)
def admin_application_create_step3(request, application_id):
    """Step 3: Transect codes and GPS"""
    application = get_object_or_404(
        GrowerApplication,
        id=application_id,
        is_admin_created=True
    )

    if not application.field:
        messages.error(request, 'Please complete Step 1 first to create the field.')
        return redirect('grower_portal:admin_application_create_step1', application_id=application.id)

    if request.method == 'POST':
        form = TransectCodesForm(request.POST, field_type=application.field.field_type)
        if form.is_valid():
            application.transect_code_1 = form.cleaned_data.get('transect_code_1', '').strip()
            application.transect_code_2 = form.cleaned_data.get('transect_code_2', '').strip()
            application.transect_code_3 = form.cleaned_data.get('transect_code_3', '').strip()
            application.transect_code_4 = form.cleaned_data.get('transect_code_4', '').strip()

            for i in range(1, 5):
                lat = form.cleaned_data.get(f'transect_{i}_latitude')
                lng = form.cleaned_data.get(f'transect_{i}_longitude')
                application.set_transect_location(i, lng, lat)

            with transaction.atomic():
                application.save()

                # If application is already submitted, mark transect codes as used
                if application.is_submitted:
                    for i in range(1, 5):
                        code = getattr(
                            application,
                            f'transect_code_{i}',
                            '').strip() if getattr(
                            application,
                            f'transect_code_{i}',
                            None) else ''
                        if code:
                            TransectCode.objects.filter(transect_code=code).update(
                                is_used=True,
                                used_in_application=application,
                                used_at=timezone.now()
                            )

            messages.success(request, 'Transect codes and coordinates saved successfully!')
            return redirect('grower_portal:admin_application_create_step4', application_id=application.id)
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

        form = TransectCodesForm(initial=initial_data, field_type=application.field.field_type)

    transect_data = []
    for i, code in enumerate(application.transect_codes):
        location = getattr(application, f'transect_{i + 1}_location', None)

        if location:
            latitude = float(location.y)
            longitude = float(location.x)
            transect_data.append({
                'index': i,
                'code': code,
                'latitude': latitude,
                'longitude': longitude
            })

    return render(request, 'grower_portal/grower/application_step3.html', {
        'application': application,
        'form': form,
        'transect_data': json.dumps(transect_data),
        'is_admin': True,
        'grower_display': application.grower_display_name,
        'has_linked_account': application.has_linked_account,
        'user_timezone': get_user_timezone(request)
    })


@login_required
@permission_required(IS_GROWERADMIN, raise_exception=True)
def admin_application_complete(request, application_id):
    """Step 5: Review & Submit - Final page with draft/submit options"""
    application = get_object_or_404(
        GrowerApplication,
        id=application_id,
        is_admin_created=True
    )

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'submit':
            if not application.transect_code_1:
                messages.error(request, 'Cannot submit: At least one transect code is required.')
                return redirect('grower_portal:admin_application_complete', application_id=application.id)

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
                        transect_obj = TransectCode.objects.get(transect_code=code, is_active=True)
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
                            return redirect('grower_portal:admin_application_complete', application_id=application.id)
                    except TransectCode.DoesNotExist:
                        messages.error(request, f'Cannot submit: Transect code {i} "{code}" is not valid or inactive.')
                        return redirect('grower_portal:admin_application_complete', application_id=application.id)

            with transaction.atomic():
                application.is_draft = False
                application.is_submitted = True
                application.submitted_at = timezone.now()
                application.save()

                for i in range(1, 5):
                    code = getattr(
                        application,
                        f'transect_code_{i}',
                        '').strip() if getattr(
                        application,
                        f'transect_code_{i}',
                        None) else ''
                    if code:
                        TransectCode.objects.filter(transect_code=code).update(
                            is_used=True,
                            used_in_application=application,
                            used_at=timezone.now()
                        )

                grower_name = application.grower_display_name
                messages.success(
                    request,
                    f'Application {application.submission_code} has been submitted on behalf of {grower_name}!'
                )

            return redirect('grower_portal:admin_application_detail', application_id=application.id)

        elif action == 'draft':
            application.is_draft = True
            application.is_submitted = False
            application.save()

            messages.success(
                request,
                f'Application {application.submission_code} has been saved as draft. You can edit and submit it later.'
            )
            return redirect('grower_portal:admin_application_detail', application_id=application.id)

    return render(request, 'grower_portal/admin/application_create/complete.html', {
        'application': application,
        'grower_display': application.grower_display_name,
        'grower_email': application.grower_display_email,
        'has_linked_account': application.has_linked_account,
        'admin_email': application.created_by_admin.email if application.created_by_admin else 'Unknown',
        'user_timezone': get_user_timezone(request)
    })
