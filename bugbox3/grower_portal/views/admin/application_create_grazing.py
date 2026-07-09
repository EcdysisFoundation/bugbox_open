from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, redirect, render

from bugbox3.core.permissions import IS_GROWERADMIN

from ...forms.grower.forms import GrazingEventAnimalFormSet, GrazingEventForm
from ...middleware import get_user_timezone
from ...models import GrazingEvent, GrowerApplication


def _admin_grazing_step(request, application, *, mode):
    assert mode in ('create', 'edit')

    if len(application.transect_codes) == 0:
        messages.error(
            request,
            'Please enter at least one transect code before recording measurements.',
        )
        if mode == 'create':
            return redirect(
                'grower_portal:admin_application_create_step3',
                application_id=application.id,
            )
        return redirect(
            'grower_portal:admin_application_edit_transects',
            application_id=application.id,
        )

    if not application.field_id:
        messages.error(request, 'Application has no field.')
        if mode == 'create':
            return redirect('grower_portal:admin_application_create_step1', application_id=application.id)
        return redirect('grower_portal:admin_application_detail', application_id=application.id)

    if application.field.field_type != 'range':
        messages.warning(request, 'Grazing events are only applicable to rangeland.')
        if mode == 'create':
            return redirect('grower_portal:admin_application_complete', application_id=application.id)
        return redirect('grower_portal:admin_application_edit_review', application_id=application.id)

    grazing_events = []
    for i in range(1, 5):
        event, _ = GrazingEvent.objects.get_or_create(
            application=application,
            event_number=i
        )
        grazing_events.append(event)

    event_forms = {}
    formsets = {}

    if request.method == 'POST':
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

            for idx in range(total_forms):
                is_deleted = request.POST.get(f'{prefix}-{idx}-DELETE', '') == 'on'
                if is_deleted:
                    continue

                class_of_animal = request.POST.get(f'{prefix}-{idx}-class_of_animal', '').strip()
                number_of_animals = request.POST.get(f'{prefix}-{idx}-number_of_animals', '').strip()
                average_weight = request.POST.get(f'{prefix}-{idx}-average_weight', '').strip()
                duration_days = request.POST.get(f'{prefix}-{idx}-duration_days', '').strip()
                rest_period_days = request.POST.get(f'{prefix}-{idx}-rest_period_days', '').strip()

                if any([class_of_animal, number_of_animals, average_weight, duration_days, rest_period_days]):
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
                if mode == 'create':
                    return redirect('grower_portal:admin_application_complete', application_id=application.id)
                return redirect('grower_portal:admin_application_edit_review', application_id=application.id)
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
        for event in grazing_events:
            event_forms[event.event_number] = GrazingEventForm(
                prefix=f'eventform_{event.event_number}',
                instance=event
            )
            formsets[event.event_number] = GrazingEventAnimalFormSet(
                instance=event,
                prefix=f'event_{event.event_number}'
            )

    admin_grazing_mode = 'create' if mode == 'create' else 'edit'
    ctx = {
        'application': application,
        'grazing_events': grazing_events,
        'event_forms': event_forms,
        'formsets': formsets,
        'user_timezone': get_user_timezone(request),
        'is_admin': True,
        'admin_grazing_mode': admin_grazing_mode,
        'grower_display': application.grower_display_name,
        'has_linked_account': application.has_linked_account,
    }
    if mode == 'edit':
        ctx['wizard_step'] = 'grazing'
    return render(request, 'grower_portal/grower/application_step5.html', ctx)


@login_required
@permission_required(IS_GROWERADMIN, raise_exception=True)
def admin_application_create_step5(request, application_id):
    application = get_object_or_404(
        GrowerApplication,
        id=application_id,
        is_admin_created=True,
    )
    return _admin_grazing_step(request, application, mode='create')


@login_required
@permission_required(IS_GROWERADMIN, raise_exception=True)
def admin_application_edit_grazing(request, application_id):
    application = get_object_or_404(GrowerApplication, id=application_id)
    if not application.is_draft:
        messages.error(request, 'Only draft applications can be edited through the wizard.')
        return redirect('grower_portal:admin_application_detail', application_id=application.id)
    return _admin_grazing_step(request, application, mode='edit')
