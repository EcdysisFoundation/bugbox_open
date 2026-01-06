from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
import json

from bugbox3.core.permissions import IS_GROWERADMIN
from ...models import GrowerApplication, ManagementPractices, Field, Farm, TransectCode
from ...forms.grower.forms import (
    ApplicationCreationForm,
    ManagementPracticesForm,
    TransectCodesForm
)
from ...constants import DEFAULT_FIELD_LATITUDE, DEFAULT_FIELD_LONGITUDE
from ...middleware import get_user_timezone


@login_required
@permission_required(IS_GROWERADMIN, raise_exception=True)
def admin_application_edit_basic(request, application_id):
    application = get_object_or_404(GrowerApplication, id=application_id)
    
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
                    
                    messages.success(request, f'Application {application.submission_code} basic info updated successfully!')
                    return redirect('grower_portal:admin_application_edit_management', application_id=application.id)
                    
            except Exception as e:
                messages.error(request, f'Error updating application: {str(e)}')
    else:
        form = ApplicationCreationForm(initial={
            'farm_name': application.field.farm.name if application.field.farm else '',
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
    
    context = {
        'application': application,
        'form': form,
        'user_timezone': get_user_timezone(request),
        'is_admin_edit': True,
    }
    
    return render(request, 'grower_portal/admin/application_edit_basic.html', context)


@login_required
@permission_required(IS_GROWERADMIN, raise_exception=True)
def admin_application_edit_management(request, application_id):
    application = get_object_or_404(GrowerApplication, id=application_id)
    
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
    }
    
    return render(request, 'grower_portal/admin/application_edit_management.html', context)


@login_required
@permission_required(IS_GROWERADMIN, raise_exception=True)
def admin_application_edit_transects(request, application_id):
    application = get_object_or_404(GrowerApplication, id=application_id)
    
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
            messages.success(request, 'Transect codes updated successfully!')
            return redirect('grower_portal:admin_application_detail', application_id=application.id)
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
    
    field_latitude = DEFAULT_FIELD_LATITUDE
    field_longitude = DEFAULT_FIELD_LONGITUDE
    
    transect_data = []
    for i, code in enumerate(application.transect_codes):
        location = getattr(application, f'transect_{i+1}_location', None)
        
        if location:
            latitude = float(location.y)
            longitude = float(location.x)
        else:
            latitude = field_latitude
            longitude = field_longitude
            
        transect_data.append({
            'index': i,
            'code': code,
            'latitude': latitude,
            'longitude': longitude
        })
    
    context = {
        'application': application,
        'form': form,
        'field_latitude': field_latitude,
        'field_longitude': field_longitude,
        'transect_data': json.dumps(transect_data),
        'user_timezone': get_user_timezone(request),
        'is_admin_edit': True,
    }
    
    return render(request, 'grower_portal/admin/application_edit_transects.html', context)


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
            code = getattr(application, f'transect_code_{i}', '').strip() if getattr(application, f'transect_code_{i}', None) else ''
            if code:
                try:
                    transect_obj = TransectCode.objects.get(transect_code=code, is_active=True)
                    if transect_obj.is_used and transect_obj.used_in_application != application:
                        messages.error(
                            request,
                            f'Cannot submit: Transect code {i} "{code}" has already been used in application {transect_obj.used_in_application.submission_code if transect_obj.used_in_application else "another application"}.'
                        )
                        return redirect('grower_portal:admin_application_edit_transects', application_id=application.id)
                except TransectCode.DoesNotExist:
                    messages.error(request, f'Cannot submit: Transect code {i} "{code}" is not valid or inactive.')
                    return redirect('grower_portal:admin_application_edit_transects', application_id=application.id)
        
        with transaction.atomic():
            application.is_draft = False
            application.is_submitted = True
            application.save()
            
            # mark transect codes as used
            for i in range(1, 5):
                code = getattr(application, f'transect_code_{i}', '').strip() if getattr(application, f'transect_code_{i}', None) else ''
                if code:
                    TransectCode.objects.filter(transect_code=code).update(
                        is_used=True,
                        used_in_application=application,
                        used_at=timezone.now()
                    )
        
        grower_name = application.grower.name if application.grower and hasattr(application.grower, 'name') else application.grower_display_name
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

