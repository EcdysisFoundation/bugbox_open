from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404, redirect, render

from bugbox3.core.permissions import IS_GROWER

from ...forms.grower.forms import ApplicationCreationForm
from ...measurement_capture import assign_field_measurements
from ...middleware import get_user_timezone
from ...models import Farm, Field, GrazingEvent, GrowerApplication, ManagementPractices, TransectMeasurement
from ...utils import get_grower_maps_json_context


@login_required
@permission_required(IS_GROWER, raise_exception=True)
def application_create(request):
    if request.method == 'POST':
        form = ApplicationCreationForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    farm, created = Farm.objects.get_or_create(
                        grower=request.user,
                        name=form.cleaned_data['farm_name']
                    )

                    existing_field = Field.objects.filter(
                        farm=farm,
                        field_name=form.cleaned_data['field_name']
                    ).first()

                    if existing_field:
                        if existing_field.field_type == form.cleaned_data['field_type']:
                            field = existing_field
                        else:
                            messages.error(
                                request,
                                f'A field named "{form.cleaned_data["field_name"]}" already exists '
                                f'with type "{existing_field.get_field_type_display()}". '
                                f'Please use a different field name or select a different farm.'
                            )
                            raise ValueError('Field type mismatch')
                    else:
                        field = Field.objects.create(
                            farm=farm,
                            field_name=form.cleaned_data['field_name'],
                            field_type=form.cleaned_data['field_type'],
                            crop_type=form.cleaned_data.get('crop_type', ''),
                            crop_subtype=form.cleaned_data.get('crop_subtype', ''),
                            crop_subtype_other=form.cleaned_data.get('crop_subtype_other', ''),
                            small_grain_type=form.cleaned_data.get('small_grain_type', ''),
                            tillage_methods=form.cleaned_data.get('tillage_methods', ''),
                            forage_varieties=form.cleaned_data.get('forage_varieties', ''),
                            rootstock_species=form.cleaned_data.get('rootstock_species', ''),
                            transitional_status=form.cleaned_data.get('transitional_status', ''),
                            years_under_management=form.cleaned_data.get('years_under_management'),
                            supports_dairy=form.cleaned_data.get('supports_dairy', False),
                            is_confined_dairy=form.cleaned_data.get('is_confined_dairy', False),
                            measurement_comments=form.cleaned_data.get('measurement_comments', '')
                        )
                        assign_field_measurements(field, form.cleaned_data)
                        if form.cleaned_data.get('orchard_crop_type'):
                            field.crop_type = form.cleaned_data.get('orchard_crop_type', '')
                        field.orchard_crop_specify = form.cleaned_data.get('orchard_crop_specify', '')
                        if form.cleaned_data.get('crop_varieties'):
                            field.crop_varieties = form.cleaned_data.get('crop_varieties', '')
                        field.save()

                    application = GrowerApplication.objects.create(
                        field=field,
                        grower=request.user,
                        date_sampled=form.cleaned_data['date_sampled']
                    )

                    messages.success(request, f'Application {application.submission_code} created successfully!')
                    return redirect('grower_portal:application_step2', application_id=application.id)

            except IntegrityError as e:
                if 'field_id_date_sampled' in str(e):
                    messages.error(
                        request,
                        f'An application already exists for field '
                        f'"{form.cleaned_data["field_name"]}" on '
                        f'{form.cleaned_data["date_sampled"].strftime("%B %d, %Y")}. '
                        f'Please choose a different date or edit the existing application from your dashboard.'
                    )
                else:
                    messages.error(
                        request,
                        'An error occurred while creating the application. '
                        'Please try again or contact support if the issue '
                        'persists.')
            except ValueError:
                pass
    else:
        form = ApplicationCreationForm()

    return render(request, 'grower_portal/grower/application_create.html', {
        'form': form,
        'user_timezone': get_user_timezone(request)
    })


@login_required
@permission_required(IS_GROWER, raise_exception=True)
def application_view(request, application_id):
    """View a submitted or draft application (read-only)"""
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

    transect_data = []
    for i, code in enumerate(application.transect_codes):
        location = getattr(application, f'transect_{i + 1}_location', None)
        if location:
            transect_data.append({
                'index': i,
                'code': code,
                'latitude': float(location.y),
                'longitude': float(location.x)
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

    context = {
        'application': application,
        'management_practices': management_practices,
        'grazing_events': grazing_events,
        'transect_measurements': transect_measurements,
        'user_timezone': get_user_timezone(request),
    }
    if application.field:
        context['json_context'] = get_grower_maps_json_context(transect_data)
    return render(request, 'grower_portal/grower/application_view.html', context)


@login_required
@permission_required(IS_GROWER, raise_exception=True)
def application_edit(request, application_id):
    application = get_object_or_404(
        GrowerApplication,
        id=application_id,
        grower=request.user
    )

    if not application.is_draft:
        messages.error(request, 'You cannot edit a submitted application.')
        return redirect('grower_portal:application_view', application_id=application.id)

    return redirect('grower_portal:application_step1', application_id=application.id)


@login_required
@permission_required(IS_GROWER, raise_exception=True)
def application_delete(request, application_id):
    """Delete a draft application"""
    application = get_object_or_404(
        GrowerApplication,
        id=application_id,
        grower=request.user
    )

    if not application.is_draft:
        messages.error(request, 'You cannot delete a submitted application.')
        return redirect('grower_portal:application_view', application_id=application.id)

    if request.method == 'POST':
        submission_code = application.submission_code
        application.delete()
        messages.success(request, f'Application {submission_code} has been deleted.')
        return redirect('grower_portal:dashboard')

    return render(request, 'grower_portal/grower/application_delete.html', {
        'application': application,
        'user_timezone': get_user_timezone(request)
    })
