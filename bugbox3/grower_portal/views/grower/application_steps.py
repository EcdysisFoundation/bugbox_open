import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from bugbox3.core.permissions import IS_GROWER

from ...constants import (
    DISTANCES_DROP_PLATE,
    INFILTROMETER_TIMES,
    POSITIONS_3POINT,
    SOIL_METRIC_CHOICES,
    VEGETATION_METRIC_CHOICES,
)
from ...forms.grower.forms import (
    ApplicationCreationForm,
    DropPlateFormSet,
    GrazingEventAnimalFormSet,
    GrazingEventForm,
    InfiltrationRingFormSet,
    InfiltrometerFormSet,
    ManagementPracticesForm,
    SoilCompactionFormSet,
    SoilFormSet,
    TransectCodesForm,
    TransectMeasurementGeneralForm,
    VegetationFormSet,
)
from ...middleware import get_user_timezone
from ...models import (
    DropPlateReading,
    Farm,
    GrazingEvent,
    GrowerApplication,
    InfiltrationRingReading,
    InfiltrometerReading,
    ManagementPractices,
    SampleCode,
    SoilCompactionReading,
    SoilReading,
    TransectMeasurement,
    VegetationReading,
)


@login_required
@permission_required(IS_GROWER, raise_exception=True)
def application_step1(request, application_id):
    application = get_object_or_404(
        GrowerApplication,
        id=application_id,
        grower=request.user
    )

    if not application.is_draft:
        messages.error(request, 'You cannot edit a submitted application.')
        return redirect('grower_portal:application_view', application_id=application.id)

    if request.method == 'POST':
        form = ApplicationCreationForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    farm, created = Farm.objects.get_or_create(
                        grower=request.user,
                        name=form.cleaned_data['farm_name']
                    )

                    field = application.field
                    field.farm = farm
                    field.field_name = form.cleaned_data['field_name']
                    field.field_type = form.cleaned_data['field_type']
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

                    messages.success(request, f'Application {application.submission_code} updated successfully!')
                    return redirect('grower_portal:application_step2', application_id=application.id)

            except IntegrityError as e:
                messages.error(request, f'Error updating application: {str(e)}')
    else:
        form = ApplicationCreationForm(initial={
            'farm_name': application.field.farm.name,
            'field_name': application.field.field_name,
            'field_type': application.field.field_type,
            'date_sampled': application.date_sampled,
            'acres_sampled': application.field.acres_sampled,
            'years_under_management': application.field.years_under_management,
            'supports_dairy': application.field.supports_dairy,
            'is_confined_dairy': application.field.is_confined_dairy,
            'measurement_comments': application.field.measurement_comments,

            'crop_type': application.field.crop_type,
            'crop_subtype': application.field.crop_subtype,
            'crop_subtype_other': application.field.crop_subtype_other,
            'small_grain_type': application.field.small_grain_type,
            'tillage_methods': application.field.tillage_methods,
            'forage_varieties': application.field.forage_varieties,
            'paddock_size': application.field.paddock_size,
            'pasture_size': application.field.pasture_size,
            'rootstock_species': application.field.rootstock_species,
            'crop_varieties': application.field.crop_varieties,
            'transitional_status': application.field.transitional_status,

            'orchard_crop_type': application.field.crop_type,
            'orchard_crop_specify': application.field.orchard_crop_specify,
        })

    return render(request, 'grower_portal/grower/application_step1.html', {
        'application': application,
        'form': form,
        'user_timezone': get_user_timezone(request)
    })


@login_required
@permission_required(IS_GROWER, raise_exception=True)
def application_step2(request, application_id):
    application = get_object_or_404(
        GrowerApplication,
        id=application_id,
        grower=request.user
    )

    practices, created = ManagementPractices.objects.get_or_create(
        application=application
    )

    if request.method == 'POST':
        form = ManagementPracticesForm(request.POST, instance=practices)
        if form.is_valid():
            form.save()
            messages.success(request, 'Management practices saved successfully!')
            return redirect('grower_portal:application_step3', application_id=application.id)
    else:
        form = ManagementPracticesForm(instance=practices)

    return render(request, 'grower_portal/grower/application_step2.html', {
        'application': application,
        'form': form,
        'user_timezone': get_user_timezone(request)
    })


@login_required
@permission_required(IS_GROWER, raise_exception=True)
def application_step3(request, application_id):
    """Step 3: Transect Codes and Location Mapping"""
    application = get_object_or_404(
        GrowerApplication,
        id=application_id,
        grower=request.user
    )

    application.field

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

            application.save()

            messages.success(request, 'Transect codes and coordinates saved successfully!')
            return redirect('grower_portal:application_step4', application_id=application.id)
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
        'user_timezone': get_user_timezone(request)
    })


@login_required
@permission_required(IS_GROWER, raise_exception=True)
def application_step4(request, application_id):
    application = get_object_or_404(
        GrowerApplication,
        id=application_id,
        grower=request.user
    )

    active_codes = application.transect_codes
    num_transects = len(active_codes)
    if num_transects == 0:
        messages.error(request, 'Please enter at least one transect code before recording measurements.')
        return redirect('grower_portal:application_step3', application_id=application.id)

    measurements = []
    for i, code in enumerate(active_codes, start=1):
        m, _ = TransectMeasurement.objects.get_or_create(
            application=application,
            transect_index=i,
            defaults={'transect_code': code}
        )
        if m.transect_code != code:
            m.transect_code = code
            m.save(update_fields=['transect_code'])
        measurements.append(m)

    transect_data = []
    all_valid = True

    should_show_dropplate = (
        application.field.field_type == 'range' or
        application.field.field_type == 'orchard' or
        (application.field.field_type == 'crop' and application.field.crop_type == 'hayfield')
    )

    if request.method == 'POST':
        with transaction.atomic():
            for m in measurements:
                data = {'measurement': m}

                general_form = TransectMeasurementGeneralForm(
                    request.POST, prefix=f'm{m.transect_index}', instance=m
                )
                data['general_form'] = general_form
                if not general_form.is_valid():
                    all_valid = False

                if should_show_dropplate:
                    dp_qs = m.drop_plate.order_by('distance_m')
                    if dp_qs.count() == 0:
                        objs = [DropPlateReading(measurement=m, distance_m=d) for d in DISTANCES_DROP_PLATE]
                        DropPlateReading.objects.bulk_create(objs)
                        dp_qs = m.drop_plate.order_by('distance_m')

                    dp_formset = DropPlateFormSet(
                        request.POST, instance=m, prefix=f'dp{m.transect_index}', queryset=dp_qs
                    )
                    data['dropplate_formset'] = dp_formset
                    if not dp_formset.is_valid():
                        all_valid = False
                else:
                    data['dropplate_formset'] = DropPlateFormSet(
                        instance=m, prefix=f'dp{m.transect_index}', queryset=DropPlateReading.objects.none()
                    )

                veg_qs = m.vegetation.order_by('metric', 'position_m')
                if veg_qs.count() == 0:
                    objs = []
                    for metric_choice, _ in VEGETATION_METRIC_CHOICES:
                        for pos in POSITIONS_3POINT:
                            objs.append(VegetationReading(
                                measurement=m, metric=metric_choice, position_m=pos
                            ))
                    VegetationReading.objects.bulk_create(objs)
                    veg_qs = m.vegetation.order_by('metric', 'position_m')

                veg_formset = VegetationFormSet(
                    request.POST, instance=m, prefix=f'veg{m.transect_index}', queryset=veg_qs
                )
                data['vegetation_formset'] = veg_formset
                if not veg_formset.is_valid():
                    all_valid = False

                soil_qs = m.soil.order_by('metric', 'position_m')
                if soil_qs.count() == 0:
                    objs = []
                    for metric_choice, _ in SOIL_METRIC_CHOICES:
                        for pos in POSITIONS_3POINT:
                            objs.append(SoilReading(
                                measurement=m, metric=metric_choice, position_m=pos
                            ))
                    SoilReading.objects.bulk_create(objs)
                    soil_qs = m.soil.order_by('metric', 'position_m')

                soil_formset = SoilFormSet(
                    request.POST, instance=m, prefix=f'soil{m.transect_index}', queryset=soil_qs
                )
                data['soil_formset'] = soil_formset
                if not soil_formset.is_valid():
                    all_valid = False

                comp_qs = m.compaction.order_by('position_m')
                if comp_qs.count() == 0:
                    objs = [SoilCompactionReading(measurement=m, position_m=pos)
                            for pos in POSITIONS_3POINT]
                    SoilCompactionReading.objects.bulk_create(objs)
                    comp_qs = m.compaction.order_by('position_m')

                comp_formset = SoilCompactionFormSet(
                    request.POST, instance=m, prefix=f'comp{m.transect_index}', queryset=comp_qs
                )
                data['compaction_formset'] = comp_formset
                if not comp_formset.is_valid():
                    all_valid = False

                infil_qs = m.infiltrometer.order_by('time_mark')
                if infil_qs.count() == 0:
                    objs = [InfiltrometerReading(measurement=m, time_mark=t)
                            for t in INFILTROMETER_TIMES]
                    InfiltrometerReading.objects.bulk_create(objs)
                    infil_qs = m.infiltrometer.order_by('time_mark')

                infil_formset = InfiltrometerFormSet(
                    request.POST, instance=m, prefix=f'infil{m.transect_index}', queryset=infil_qs
                )
                data['infiltrometer_formset'] = infil_formset
                if not infil_formset.is_valid():
                    all_valid = False

                ring_qs = m.infiltration_ring.order_by('pour_number')
                if ring_qs.count() == 0:
                    objs = [
                        InfiltrationRingReading(measurement=m, pour_number=1),
                        InfiltrationRingReading(measurement=m, pour_number=2)
                    ]
                    InfiltrationRingReading.objects.bulk_create(objs)
                    ring_qs = m.infiltration_ring.order_by('pour_number')

                ring_formset = InfiltrationRingFormSet(
                    request.POST, instance=m, prefix=f'ring{m.transect_index}', queryset=ring_qs
                )
                data['ring_formset'] = ring_formset
                if not ring_formset.is_valid():
                    all_valid = False

                transect_data.append(data)

            if all_valid:
                for data in transect_data:
                    data['general_form'].save()
                    if should_show_dropplate:
                        data['dropplate_formset'].save()
                    data['vegetation_formset'].save()
                    data['soil_formset'].save()
                    data['compaction_formset'].save()
                    data['infiltrometer_formset'].save()
                    data['ring_formset'].save()

                messages.success(request, 'Transect measurements saved successfully!')
                if application.field.field_type == 'range':
                    return redirect('grower_portal:application_step5', application_id=application.id)
                else:
                    return redirect('grower_portal:application_step6', application_id=application.id)
            else:
                messages.error(request, 'Please correct the errors below.')

    else:
        for m in measurements:
            data = {'measurement': m}

            data['general_form'] = TransectMeasurementGeneralForm(
                prefix=f'm{m.transect_index}', instance=m
            )

            if should_show_dropplate:
                dp_qs = m.drop_plate.order_by('distance_m')
                if dp_qs.count() == 0:
                    objs = [DropPlateReading(measurement=m, distance_m=d) for d in DISTANCES_DROP_PLATE]
                    DropPlateReading.objects.bulk_create(objs)
                    dp_qs = m.drop_plate.order_by('distance_m')
                data['dropplate_formset'] = DropPlateFormSet(
                    instance=m, prefix=f'dp{m.transect_index}', queryset=dp_qs
                )
            else:
                data['dropplate_formset'] = DropPlateFormSet(
                    instance=m, prefix=f'dp{m.transect_index}', queryset=DropPlateReading.objects.none()
                )

            veg_qs = m.vegetation.order_by('metric', 'position_m')
            if veg_qs.count() == 0:
                objs = []
                for metric_choice, _ in VEGETATION_METRIC_CHOICES:
                    for pos in POSITIONS_3POINT:
                        objs.append(VegetationReading(
                            measurement=m, metric=metric_choice, position_m=pos
                        ))
                VegetationReading.objects.bulk_create(objs)
                veg_qs = m.vegetation.order_by('metric', 'position_m')
            data['vegetation_formset'] = VegetationFormSet(
                instance=m, prefix=f'veg{m.transect_index}', queryset=veg_qs
            )

            soil_qs = m.soil.order_by('metric', 'position_m')
            if soil_qs.count() == 0:
                objs = []
                for metric_choice, _ in SOIL_METRIC_CHOICES:
                    for pos in POSITIONS_3POINT:
                        objs.append(SoilReading(
                            measurement=m, metric=metric_choice, position_m=pos
                        ))
                SoilReading.objects.bulk_create(objs)
                soil_qs = m.soil.order_by('metric', 'position_m')
            data['soil_formset'] = SoilFormSet(
                instance=m, prefix=f'soil{m.transect_index}', queryset=soil_qs
            )

            comp_qs = m.compaction.order_by('position_m')
            if comp_qs.count() == 0:
                objs = [SoilCompactionReading(measurement=m, position_m=pos)
                        for pos in POSITIONS_3POINT]
                SoilCompactionReading.objects.bulk_create(objs)
                comp_qs = m.compaction.order_by('position_m')
            data['compaction_formset'] = SoilCompactionFormSet(
                instance=m, prefix=f'comp{m.transect_index}', queryset=comp_qs
            )

            infil_qs = m.infiltrometer.order_by('time_mark')
            if infil_qs.count() == 0:
                objs = [InfiltrometerReading(measurement=m, time_mark=t)
                        for t in INFILTROMETER_TIMES]
                InfiltrometerReading.objects.bulk_create(objs)
                infil_qs = m.infiltrometer.order_by('time_mark')
            data['infiltrometer_formset'] = InfiltrometerFormSet(
                instance=m, prefix=f'infil{m.transect_index}', queryset=infil_qs
            )

            ring_qs = m.infiltration_ring.order_by('pour_number')
            if ring_qs.count() == 0:
                objs = [
                    InfiltrationRingReading(measurement=m, pour_number=1),
                    InfiltrationRingReading(measurement=m, pour_number=2)
                ]
                InfiltrationRingReading.objects.bulk_create(objs)
                ring_qs = m.infiltration_ring.order_by('pour_number')
            data['ring_formset'] = InfiltrationRingFormSet(
                instance=m, prefix=f'ring{m.transect_index}', queryset=ring_qs
            )

            transect_data.append(data)

    return render(request, 'grower_portal/grower/application_step4.html', {
        'application': application,
        'transect_data': transect_data,
        'user_timezone': get_user_timezone(request)
    })


@login_required
@permission_required(IS_GROWER, raise_exception=True)
def application_step5(request, application_id):
    """Step 5: Grazing Events (rangeland only)"""
    application = get_object_or_404(
        GrowerApplication,
        id=application_id,
        grower=request.user
    )

    if application.field.field_type != 'range':
        messages.warning(request, 'Grazing events are only applicable to rangeland.')
        return redirect('grower_portal:application_step6', application_id=application.id)

    grazing_events = []
    for i in range(1, 5):
        event, _ = GrazingEvent.objects.get_or_create(
            application=application,
            event_number=i
        )
        grazing_events.append(event)

    if request.method == 'POST':
        event_forms = {}
        formsets = {}
        formsets_has_data = {}
        all_valid = True
        formset_errors = {}

        for event in grazing_events:
            event_form = GrazingEventForm(
                request.POST,
                prefix=f'eventform_{event.event_number}',
                instance=event
            )
            event_forms[event.event_number] = event_form
            if not event_form.is_valid():
                all_valid = False
                formset_errors[event.event_number] = event_form.errors

            formset = GrazingEventAnimalFormSet(
                request.POST,
                instance=event,
                prefix=f'event_{event.event_number}'
            )
            formsets[event.event_number] = formset

            prefix = f'event_{event.event_number}'
            has_any_data = False
            total_forms = int(request.POST.get(f'{prefix}-TOTAL_FORMS', '0'))

            for i in range(total_forms):
                is_deleted = request.POST.get(f'{prefix}-{i}-DELETE', '') == 'on'
                if is_deleted:
                    continue

                class_of_animal = request.POST.get(f'{prefix}-{i}-class_of_animal', '').strip()
                number_of_animals = request.POST.get(f'{prefix}-{i}-number_of_animals', '').strip()
                average_weight_lbs = request.POST.get(f'{prefix}-{i}-average_weight_lbs', '').strip()
                duration_days = request.POST.get(f'{prefix}-{i}-duration_days', '').strip()
                rest_period_days = request.POST.get(f'{prefix}-{i}-rest_period_days', '').strip()

                if any([class_of_animal, number_of_animals, average_weight_lbs, duration_days, rest_period_days]):
                    has_any_data = True
                    break

            formsets_has_data[event.event_number] = has_any_data

            if has_any_data:
                if not formset.is_valid():
                    all_valid = False
                    formset_errors[event.event_number] = formset.errors

        if all_valid:
            try:
                for form in event_forms.values():
                    form.save()
                for event_num, formset in formsets.items():
                    if formsets_has_data.get(event_num, False):
                        if formset.is_valid():
                            formset.save()
                        else:
                            raise ValueError(f"Formset validation failed for event {event_num}: {formset.errors}")
                    else:
                        formset.is_valid()
                        formset.save()
                messages.success(request, 'Grazing events saved successfully!')
                return redirect('grower_portal:application_step6', application_id=application.id)
            except Exception as e:
                messages.error(request, f'Error saving grazing events: {str(e)}')
        else:
            error_details = []
            for event_num, errors in formset_errors.items():
                error_details.append(f"Event {event_num}: {errors}")
            messages.error(request, 'Please correct the errors below.')
            if error_details:
                messages.error(request, f'Details: {"; ".join(error_details)}')
    else:
        event_forms = {}
        formsets = {}
        for event in grazing_events:
            event_forms[event.event_number] = GrazingEventForm(
                prefix=f'eventform_{event.event_number}',
                instance=event
            )
            formsets[event.event_number] = GrazingEventAnimalFormSet(
                instance=event,
                prefix=f'event_{event.event_number}'
            )

    return render(request, 'grower_portal/grower/application_step5.html', {
        'application': application,
        'grazing_events': grazing_events,
        'event_forms': event_forms,
        'formsets': formsets,
        'user_timezone': get_user_timezone(request)
    })


@login_required
@permission_required(IS_GROWER, raise_exception=True)
def application_step6(request, application_id):
    """Step 6: Review & Submit (rangeland) or Step 5: Review & Submit (non-rangeland)"""
    application = get_object_or_404(
        GrowerApplication,
        id=application_id,
        grower=request.user
    )

    try:
        management_practices = ManagementPractices.objects.get(application=application)
    except ManagementPractices.DoesNotExist:
        management_practices = None

    grazing_events = GrazingEvent.objects.filter(application=application).prefetch_related(
        'animals').order_by('event_number') if application.field.field_type == 'range' else []

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'submit':
            if not application.date_sampled:
                messages.error(
                    request,
                    'Date sampled is required before submitting. Please complete step 1 '
                    'and set the date when samples were collected.'
                )
                return redirect('grower_portal:application_step1', application_id=application.id)
            application.is_submitted = True
            application.is_draft = False
            try:
                application.save()
            except ValidationError as e:
                messages.error(request, e.messages[0] if e.messages else str(e))
                return redirect('grower_portal:application_step6', application_id=application.id)
            for i in range(1, 5):
                code = getattr(application, f'transect_code_{i}', '').strip()
                if code:
                    SampleCode.objects.filter(code=code).update(
                        is_used=True,
                        used_in_application=application,
                        used_at=timezone.now()
                    )

            messages.success(request, f'Application {application.submission_code} submitted successfully!')
            return redirect('grower_portal:dashboard')
        elif action == 'save_draft':
            application.is_draft = True
            application.save()
            messages.success(request, f'Application {application.submission_code} saved as draft.')
            return redirect('grower_portal:dashboard')

    application.field

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

    transect_measurements = TransectMeasurement.objects.filter(
        application=application
    ).prefetch_related(
        'drop_plate',
        'vegetation',
        'soil',
        'compaction',
        'infiltrometer',
        'infiltration_ring'
    ).order_by('transect_index')

    return render(request, 'grower_portal/grower/application_step6.html', {
        'application': application,
        'management_practices': management_practices,
        'grazing_events': grazing_events,
        'transect_measurements': transect_measurements,
        'transect_data': json.dumps(transect_data),
        'user_timezone': get_user_timezone(request)
    })
