from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db import IntegrityError, transaction
import json

from bugbox3.core.permissions import IS_GROWER
from ...models import (
    Farm, Field, GrowerApplication,
    ManagementPractices, GrazingEvent
)
from ...forms.grower.forms import ApplicationCreationForm
from ...constants import DEFAULT_FIELD_LATITUDE, DEFAULT_FIELD_LONGITUDE
from ...middleware import get_user_timezone


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
                            paddock_size=form.cleaned_data.get('paddock_size', ''),
                            rootstock_species=form.cleaned_data.get('rootstock_species', ''),
                            transitional_status=form.cleaned_data.get('transitional_status', ''),
                            acres_sampled=form.cleaned_data.get('acres_sampled'),
                            years_under_management=form.cleaned_data.get('years_under_management'),
                            supports_dairy=form.cleaned_data.get('supports_dairy', False),
                            is_confined_dairy=form.cleaned_data.get('is_confined_dairy', False),
                            measurement_comments=form.cleaned_data.get('measurement_comments', '')
                        )
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
                        f'An application already exists for field "{form.cleaned_data["field_name"]}" on {form.cleaned_data["date_sampled"].strftime("%B %d, %Y")}. '
                        f'Please choose a different date or edit the existing application from your dashboard.'
                    )
                else:
                    messages.error(
                        request,
                        'An error occurred while creating the application. Please try again or contact support if the issue persists.'
                    )
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
        management_practices = ManagementPractices.objects.get(field=application.field)
    except ManagementPractices.DoesNotExist:
        management_practices = None
    
    grazing_events = GrazingEvent.objects.filter(application=application).order_by('event_number') if application.field.field_type == 'range' else []
    
    field = application.field
    field_latitude = float(field.latitude) if field.latitude else DEFAULT_FIELD_LATITUDE
    field_longitude = float(field.longitude) if field.longitude else DEFAULT_FIELD_LONGITUDE
    
    transect_data = []
    for i, code in enumerate(application.transect_codes):
        transect_data.append({
            'index': i,
            'code': code,
            'latitude': field_latitude,
            'longitude': field_longitude
        })
    
    return render(request, 'grower_portal/grower/application_view.html', {
        'application': application,
        'management_practices': management_practices,
        'grazing_events': grazing_events,
        'field_latitude': field_latitude,
        'field_longitude': field_longitude,
        'transect_data': json.dumps(transect_data),
        'user_timezone': get_user_timezone(request)
    })


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

