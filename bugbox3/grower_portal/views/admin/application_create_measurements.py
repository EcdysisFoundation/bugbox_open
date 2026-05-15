from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, redirect, render

from bugbox3.core.permissions import IS_GROWERADMIN

from ...constants import (
    DISTANCES_DROP_PLATE,
    INFILTROMETER_TIMES,
    POSITIONS_3POINT,
    SOIL_METRIC_CHOICES,
    VEGETATION_METRIC_CHOICES,
)
from ...forms.grower.forms import (
    DropPlateFormSet,
    InfiltrationRingFormSet,
    InfiltrometerFormSet,
    SoilCompactionFormSet,
    SoilFormSet,
    TransectMeasurementGeneralForm,
    VegetationFormSet,
)
from ...middleware import get_user_timezone
from ...models import (
    DropPlateReading,
    GrowerApplication,
    InfiltrationRingReading,
    InfiltrometerReading,
    SoilCompactionReading,
    SoilReading,
    TransectMeasurement,
    VegetationReading,
)


def _admin_application_measurements_step(request, application, *, mode):
    """Shared Step 4 GET/POST. mode is 'create' (admin wizard) or 'edit' (any draft app)."""
    assert mode in ('create', 'edit')

    active_codes = application.transect_codes
    if len(active_codes) == 0:
        messages.error(request, 'Please enter at least one transect code before recording measurements.')
        if mode == 'create':
            return redirect('grower_portal:admin_application_create_step3', application_id=application.id)
        return redirect('grower_portal:admin_application_edit_transects', application_id=application.id)

    should_show_dropplate = (
        application.field and (
            application.field.field_type == 'range' or
            application.field.field_type == 'orchard' or
            (application.field.field_type == 'crop' and application.field.crop_type == 'hayfield')
        )
    )

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

        if should_show_dropplate and m.drop_plate.count() == 0:
            objs = [DropPlateReading(measurement=m, distance_m=d) for d in DISTANCES_DROP_PLATE]
            DropPlateReading.objects.bulk_create(objs)

        if m.vegetation.count() == 0:
            objs = []
            for metric_choice, _ in VEGETATION_METRIC_CHOICES:
                for pos in POSITIONS_3POINT:
                    objs.append(VegetationReading(
                        measurement=m, metric=metric_choice, position_m=pos
                    ))
            VegetationReading.objects.bulk_create(objs)

        if m.soil.count() == 0:
            objs = []
            for metric_choice, _ in SOIL_METRIC_CHOICES:
                for pos in POSITIONS_3POINT:
                    objs.append(SoilReading(
                        measurement=m, metric=metric_choice, position_m=pos
                    ))
            SoilReading.objects.bulk_create(objs)

        if m.compaction.count() == 0:
            objs = [SoilCompactionReading(measurement=m, position_m=pos)
                    for pos in POSITIONS_3POINT]
            SoilCompactionReading.objects.bulk_create(objs)

        if m.infiltrometer.count() == 0:
            objs = [InfiltrometerReading(measurement=m, time_mark=t)
                    for t in INFILTROMETER_TIMES]
            InfiltrometerReading.objects.bulk_create(objs)

        if m.infiltration_ring.count() == 0:
            objs = [
                InfiltrationRingReading(measurement=m, pour_number=1),
                InfiltrationRingReading(measurement=m, pour_number=2)
            ]
            InfiltrationRingReading.objects.bulk_create(objs)

    if request.method == 'POST':
        transect_data = []
        all_valid = True
        validation_errors = []

        for m in measurements:
            data = {'measurement': m}

            general_form = TransectMeasurementGeneralForm(
                request.POST, prefix=f'm{m.transect_index}', instance=m
            )
            data['general_form'] = general_form
            if not general_form.is_valid():
                all_valid = False
                validation_errors.append(f"Transect {m.transect_index} - General form errors: {general_form.errors}")

            if should_show_dropplate:
                dp_qs = m.drop_plate.order_by('distance_m')
                dropplate_formset = DropPlateFormSet(
                    request.POST, instance=m, prefix=f'dp{m.transect_index}', queryset=dp_qs
                )
                data['dropplate_formset'] = dropplate_formset
                if not dropplate_formset.is_valid():
                    all_valid = False
                    validation_errors.append(
                        f"Transect {m.transect_index} - Drop plate formset errors: {dropplate_formset.errors}")
            else:
                data['dropplate_formset'] = DropPlateFormSet(
                    request.POST, instance=m, prefix=f'dp{m.transect_index}', queryset=DropPlateReading.objects.none()
                )
                if not data['dropplate_formset'].is_valid():
                    total_forms = int(request.POST.get(f'dp{m.transect_index}-TOTAL_FORMS', '0'))
                    if total_forms > 0:
                        all_valid = False
                        validation_errors.append(
                            f"Transect {
                                m.transect_index} - Drop plate formset should not be submitted for this field type")

            veg_qs = m.vegetation.order_by('metric', 'position_m')
            vegetation_formset = VegetationFormSet(
                request.POST, instance=m, prefix=f'veg{m.transect_index}', queryset=veg_qs
            )
            data['vegetation_formset'] = vegetation_formset
            if not vegetation_formset.is_valid():
                all_valid = False
                validation_errors.append(
                    f"Transect {m.transect_index} - Vegetation formset errors: {vegetation_formset.errors}")

            soil_qs = m.soil.order_by('metric', 'position_m')
            soil_formset = SoilFormSet(
                request.POST, instance=m, prefix=f'soil{m.transect_index}', queryset=soil_qs
            )
            data['soil_formset'] = soil_formset
            if not soil_formset.is_valid():
                all_valid = False
                validation_errors.append(f"Transect {m.transect_index} - Soil formset errors: {soil_formset.errors}")

            comp_qs = m.compaction.order_by('position_m')
            compaction_formset = SoilCompactionFormSet(
                request.POST, instance=m, prefix=f'comp{m.transect_index}', queryset=comp_qs
            )
            data['compaction_formset'] = compaction_formset
            if not compaction_formset.is_valid():
                all_valid = False
                validation_errors.append(
                    f"Transect {m.transect_index} - Compaction formset errors: {compaction_formset.errors}")

            infil_qs = m.infiltrometer.order_by('time_mark')
            infiltrometer_formset = InfiltrometerFormSet(
                request.POST, instance=m, prefix=f'infil{m.transect_index}', queryset=infil_qs
            )
            data['infiltrometer_formset'] = infiltrometer_formset
            if not infiltrometer_formset.is_valid():
                all_valid = False
                validation_errors.append(
                    f"Transect {m.transect_index} - Infiltrometer formset errors: {infiltrometer_formset.errors}")

            ring_qs = m.infiltration_ring.order_by('pour_number')
            ring_formset = InfiltrationRingFormSet(
                request.POST, instance=m, prefix=f'ring{m.transect_index}', queryset=ring_qs
            )
            data['ring_formset'] = ring_formset
            if not ring_formset.is_valid():
                all_valid = False
                validation_errors.append(f"Transect {m.transect_index} - Ring formset errors: {ring_formset.errors}")

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

            messages.success(request, 'All measurements saved successfully!')
            if mode == 'create':
                if application.field_id and application.field.field_type == 'range':
                    return redirect(
                        'grower_portal:admin_application_create_step5',
                        application_id=application.id,
                    )
                return redirect('grower_portal:admin_application_complete', application_id=application.id)
            if application.field_id and application.field.field_type == 'range':
                return redirect('grower_portal:admin_application_edit_grazing', application_id=application.id)
            return redirect('grower_portal:admin_application_detail', application_id=application.id)
        messages.error(request, 'Please correct the errors below.')
        for error in validation_errors:
            messages.error(request, error)
    else:
        transect_data = []
        for m in measurements:
            data = {'measurement': m}

            data['general_form'] = TransectMeasurementGeneralForm(
                prefix=f'm{m.transect_index}', instance=m
            )

            if should_show_dropplate:
                dp_qs = m.drop_plate.order_by('distance_m')
                data['dropplate_formset'] = DropPlateFormSet(
                    instance=m, prefix=f'dp{m.transect_index}', queryset=dp_qs
                )
            else:
                data['dropplate_formset'] = DropPlateFormSet(
                    instance=m, prefix=f'dp{m.transect_index}', queryset=DropPlateReading.objects.none()
                )

            veg_qs = m.vegetation.order_by('metric', 'position_m')
            data['vegetation_formset'] = VegetationFormSet(
                instance=m, prefix=f'veg{m.transect_index}', queryset=veg_qs
            )

            soil_qs = m.soil.order_by('metric', 'position_m')
            data['soil_formset'] = SoilFormSet(
                instance=m, prefix=f'soil{m.transect_index}', queryset=soil_qs
            )

            comp_qs = m.compaction.order_by('position_m')
            data['compaction_formset'] = SoilCompactionFormSet(
                instance=m, prefix=f'comp{m.transect_index}', queryset=comp_qs
            )

            infil_qs = m.infiltrometer.order_by('time_mark')
            data['infiltrometer_formset'] = InfiltrometerFormSet(
                instance=m, prefix=f'infil{m.transect_index}', queryset=infil_qs
            )

            ring_qs = m.infiltration_ring.order_by('pour_number')
            data['ring_formset'] = InfiltrationRingFormSet(
                instance=m, prefix=f'ring{m.transect_index}', queryset=ring_qs
            )

            transect_data.append(data)

    ctx = {
        'application': application,
        'transect_data': transect_data,
        'is_admin': True,
        'admin_measurements_mode': mode,
        'grower_display': application.grower_display_name,
        'has_linked_account': application.has_linked_account,
        'user_timezone': get_user_timezone(request),
    }
    if mode == 'edit':
        ctx['wizard_step'] = 'measurements'
    return render(request, 'grower_portal/grower/application_step4.html', ctx)


@login_required
@permission_required(IS_GROWERADMIN, raise_exception=True)
def admin_application_create_step4(request, application_id):
    """Step 4: Measurements (admin create wizard only)."""
    application = get_object_or_404(
        GrowerApplication,
        id=application_id,
        is_admin_created=True
    )
    return _admin_application_measurements_step(request, application, mode='create')


@login_required
@permission_required(IS_GROWERADMIN, raise_exception=True)
def admin_application_edit_measurements(request, application_id):
    """Step 4: Edit transect measurements for any draft application."""
    application = get_object_or_404(GrowerApplication, id=application_id)
    if not application.is_draft:
        messages.error(request, 'Transect measurements can only be edited for draft applications.')
        return redirect('grower_portal:admin_application_detail', application_id=application.id)
    return _admin_application_measurements_step(request, application, mode='edit')
