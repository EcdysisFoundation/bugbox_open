from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.http import Http404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.forms import modelformset_factory
from django.db import IntegrityError, transaction
import json

from bugbox3.core.permissions import IS_GROWER_USER, IS_GROWER
from ...models import (
    GrowerProfile, Farm, Field, GrowerApplication,
    ManagementPractices, GrazingEvent, TransectCode
)
from ...forms.grower.forms import (
    GrowerProfileCompletionForm, ApplicationCreationForm,
    ManagementPracticesForm, TransectCodesForm, GrazingEventForm,
    GrazingEventAnimalFormSet
)
from ...constants import DEFAULT_FIELD_LATITUDE, DEFAULT_FIELD_LONGITUDE
from ...middleware import get_user_timezone

User = get_user_model()


def grant_full_grower_permissions(user):
    """Grant full IS_GROWER permissions to a user after profile completion"""
    permissions_to_add = []
    for perm_string in IS_GROWER:
        app_label, codename = perm_string.split('.')
        try:
            perm = Permission.objects.get(
                content_type__app_label=app_label,
                codename=codename
            )
            permissions_to_add.append(perm)
        except Permission.DoesNotExist:
            pass
    
    if permissions_to_add:
        user.user_permissions.add(*permissions_to_add)


@login_required
@permission_required(IS_GROWER_USER, raise_exception=True)
def profile_complete(request):
    """One-time profile completion form for new growers"""
    try:
        grower_profile = request.user.grower_profile
        if grower_profile.profile_completed:
            return redirect('grower_portal:dashboard')
    except GrowerProfile.DoesNotExist:
        pass

    if request.method == 'POST':
        action = request.POST.get('action', 'complete')
        
        if action == 'skip':
            grower_profile, created = GrowerProfile.objects.get_or_create(
                user=request.user,
                defaults={'profile_completed': True}
            )
            if not created:
                grower_profile.profile_completed = True
                grower_profile.save()
            
            grant_full_grower_permissions(request.user)
            
            messages.info(request, 'Profile completion skipped. You can complete it later from your dashboard.')
            return redirect('grower_portal:dashboard')
        
        else:
            form = GrowerProfileCompletionForm(request.POST)
            if form.is_valid():
                grower_profile, created = GrowerProfile.objects.get_or_create(
                    user=request.user,
                    defaults=form.cleaned_data
                )
                if not created:
                    for field, value in form.cleaned_data.items():
                        setattr(grower_profile, field, value)
                
                grower_profile.profile_completed = True
                grower_profile.save()
                grant_full_grower_permissions(request.user)
                
                messages.success(request, 'Your grower profile has been completed successfully!')
                return redirect('grower_portal:dashboard')
    else:
        form = GrowerProfileCompletionForm()

    return render(request, 'grower_portal/grower/profile_complete.html', {
        'form': form,
        'user_timezone': get_user_timezone(request)
    })


@login_required
@permission_required(IS_GROWER, raise_exception=True)
def dashboard(request):
    """Main grower dashboard"""
    try:
        grower_profile = request.user.grower_profile
    except GrowerProfile.DoesNotExist:
        return redirect('grower_portal:profile_complete')
    
    if not grower_profile.profile_completed:
        return redirect('grower_portal:profile_complete')
    
    applications = GrowerApplication.objects.filter(grower=request.user).order_by('-date_sampled')
    
    return render(request, 'grower_portal/grower/dashboard.html', {
        'grower_profile': grower_profile,
        'applications': applications,
        'user_timezone': get_user_timezone(request)
    })


@login_required
@permission_required(IS_GROWER, raise_exception=True)
def profile_edit(request):
    """Edit grower profile"""
    try:
        grower_profile = request.user.grower_profile
    except GrowerProfile.DoesNotExist:
        return redirect('grower_portal:profile_complete')
    
    if request.method == 'POST':
        form = GrowerProfileCompletionForm(request.POST, instance=grower_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('grower_portal:dashboard')
    else:
        form = GrowerProfileCompletionForm(instance=grower_profile)

    return render(request, 'grower_portal/grower/profile_complete.html', {
        'form': form,
        'is_edit': True,
        'user_timezone': get_user_timezone(request)
    })


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
                            latitude=form.cleaned_data.get('latitude'),
                            longitude=form.cleaned_data.get('longitude'),
                            crop_type=form.cleaned_data.get('crop_type', ''),
                            crop_subtype=form.cleaned_data.get('crop_subtype', ''),
                            crop_subtype_other=form.cleaned_data.get('crop_subtype_other', ''),
                            small_grain_type=form.cleaned_data.get('small_grain_type', ''),
                            uses_broad_fork=form.cleaned_data.get('uses_broad_fork', False),
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
                    field.latitude = form.cleaned_data.get('latitude')
                    field.longitude = form.cleaned_data.get('longitude')
                    field.acres_sampled = form.cleaned_data.get('acres_sampled')
                    field.years_under_management = form.cleaned_data.get('years_under_management')
                    field.supports_dairy = form.cleaned_data.get('supports_dairy', False)
                    field.is_confined_dairy = form.cleaned_data.get('is_confined_dairy', False)
                    field.measurement_comments = form.cleaned_data.get('measurement_comments', '')
                    
                    field.crop_type = form.cleaned_data.get('crop_type', '')
                    field.crop_subtype = form.cleaned_data.get('crop_subtype', '')
                    field.crop_subtype_other = form.cleaned_data.get('crop_subtype_other', '')
                    field.small_grain_type = form.cleaned_data.get('small_grain_type', '')
                    field.uses_broad_fork = form.cleaned_data.get('uses_broad_fork', False)
                    
                    if form.cleaned_data.get('orchard_crop_type'):
                        field.crop_type = form.cleaned_data.get('orchard_crop_type', '')
                    if form.cleaned_data.get('orchard_crop_subtype'):
                        field.crop_subtype = form.cleaned_data.get('orchard_crop_subtype', '')
                    if form.cleaned_data.get('orchard_crop_subtype_other'):
                        field.crop_subtype_other = form.cleaned_data.get('orchard_crop_subtype_other', '')
                    if form.cleaned_data.get('orchard_small_grain_type'):
                        field.small_grain_type = form.cleaned_data.get('orchard_small_grain_type', '')
                    if form.cleaned_data.get('orchard_uses_broad_fork'):
                        field.uses_broad_fork = form.cleaned_data.get('orchard_uses_broad_fork', False)
                    
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
            'latitude': application.field.latitude,
            'longitude': application.field.longitude,
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
            'uses_broad_fork': application.field.uses_broad_fork,
            'forage_varieties': application.field.forage_varieties,
            'paddock_size': application.field.paddock_size,
            'pasture_size': application.field.pasture_size,
            'rootstock_species': application.field.rootstock_species,
            'crop_varieties': application.field.crop_varieties,
            'transitional_status': application.field.transitional_status,
            
            'orchard_crop_type': application.field.crop_type,
            'orchard_crop_subtype': application.field.crop_subtype,
            'orchard_crop_subtype_other': application.field.crop_subtype_other,
            'orchard_small_grain_type': application.field.small_grain_type,
            'orchard_uses_broad_fork': application.field.uses_broad_fork
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
        field=application.field
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
    
    field = application.field
    field_latitude = float(field.latitude) if field.latitude else DEFAULT_FIELD_LATITUDE
    field_longitude = float(field.longitude) if field.longitude else DEFAULT_FIELD_LONGITUDE
    
    if request.method == 'POST':
        form = TransectCodesForm(request.POST, field_type=application.field.field_type)
        if form.is_valid():
            application.transect_code_1 = form.cleaned_data.get('transect_code_1', '').strip()
            application.transect_code_2 = form.cleaned_data.get('transect_code_2', '').strip()
            application.transect_code_3 = form.cleaned_data.get('transect_code_3', '').strip()
            application.transect_code_4 = form.cleaned_data.get('transect_code_4', '').strip()
            
            application.transect_1_latitude = form.cleaned_data.get('transect_1_latitude')
            application.transect_1_longitude = form.cleaned_data.get('transect_1_longitude')
            application.transect_2_latitude = form.cleaned_data.get('transect_2_latitude')
            application.transect_2_longitude = form.cleaned_data.get('transect_2_longitude')
            application.transect_3_latitude = form.cleaned_data.get('transect_3_latitude')
            application.transect_3_longitude = form.cleaned_data.get('transect_3_longitude')
            application.transect_4_latitude = form.cleaned_data.get('transect_4_latitude')
            application.transect_4_longitude = form.cleaned_data.get('transect_4_longitude')
            
            application.save()
            
            messages.success(request, 'Transect codes and coordinates saved successfully!')
            if application.field.field_type == 'range':
                return redirect('grower_portal:application_step4', application_id=application.id)
            else:
                return redirect('grower_portal:application_step5', application_id=application.id)
    else:
        initial_data = {
            'transect_code_1': application.transect_code_1 or '',
            'transect_code_2': application.transect_code_2 or '',
            'transect_code_3': application.transect_code_3 or '',
            'transect_code_4': application.transect_code_4 or '',
            'transect_1_latitude': application.transect_1_latitude,
            'transect_1_longitude': application.transect_1_longitude,
            'transect_2_latitude': application.transect_2_latitude,
            'transect_2_longitude': application.transect_2_longitude,
            'transect_3_latitude': application.transect_3_latitude,
            'transect_3_longitude': application.transect_3_longitude,
            'transect_4_latitude': application.transect_4_latitude,
            'transect_4_longitude': application.transect_4_longitude,
        }
        
        form = TransectCodesForm(initial=initial_data, field_type=application.field.field_type)
    
    transect_data = []
    for i, code in enumerate(application.transect_codes):
        lat_field = getattr(application, f'transect_{i+1}_latitude', None)
        lng_field = getattr(application, f'transect_{i+1}_longitude', None)
        
        if lat_field and lng_field:
            latitude = float(lat_field)
            longitude = float(lng_field)
        else:
            latitude = field_latitude
            longitude = field_longitude
            
        transect_data.append({
            'index': i,
            'code': code,
            'latitude': latitude,
            'longitude': longitude
        })
    
    return render(request, 'grower_portal/grower/application_step3.html', {
        'application': application,
        'form': form,
        'field_latitude': field_latitude,
        'field_longitude': field_longitude,
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
    
    if application.field.field_type != 'range':
        messages.warning(request, 'Grazing events are only applicable to rangeland.')
        return redirect('grower_portal:application_step5', application_id=application.id)
    
    grazing_events = []
    for i in range(1, 5):
        event, _ = GrazingEvent.objects.get_or_create(
            application=application,
            event_number=i
        )
        grazing_events.append(event)
    
    if request.method == 'POST':
        formsets = {}
        all_valid = True
        
        for event in grazing_events:
            formset = GrazingEventAnimalFormSet(
                request.POST,
                instance=event,
                prefix=f'event_{event.event_number}'
            )
            formsets[event.event_number] = formset
            if not formset.is_valid():
                all_valid = False
        
        if all_valid:
            for formset in formsets.values():
                formset.save()
            messages.success(request, 'Grazing events saved successfully!')
            return redirect('grower_portal:application_step5', application_id=application.id)
    else:
        formsets = {}
        for event in grazing_events:
            formsets[event.event_number] = GrazingEventAnimalFormSet(
                instance=event,
                prefix=f'event_{event.event_number}'
            )
    
    return render(request, 'grower_portal/grower/application_step4.html', {
        'application': application,
        'grazing_events': grazing_events,
        'formsets': formsets,
        'user_timezone': get_user_timezone(request)
    })


@login_required
@permission_required(IS_GROWER, raise_exception=True)
def application_step5(request, application_id):
    application = get_object_or_404(
        GrowerApplication,
        id=application_id,
        grower=request.user
    )
    
    try:
        management_practices = ManagementPractices.objects.get(field=application.field)
    except ManagementPractices.DoesNotExist:
        management_practices = None
    
    grazing_events = GrazingEvent.objects.filter(application=application).prefetch_related('animals').order_by('event_number') if application.field.field_type == 'range' else []
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'submit':
            application.is_submitted = True
            application.is_draft = False
            application.save()
            
            from django.utils import timezone
            for i in range(1, 5):
                code = getattr(application, f'transect_code_{i}', '').strip()
                if code:
                    TransectCode.objects.filter(transect_code=code).update(
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
    
    field = application.field
    field_latitude = float(field.latitude) if field.latitude else DEFAULT_FIELD_LATITUDE
    field_longitude = float(field.longitude) if field.longitude else DEFAULT_FIELD_LONGITUDE
    
    transect_data = []
    for i, code in enumerate(application.transect_codes):
        lat_field = getattr(application, f'transect_{i+1}_latitude', None)
        lng_field = getattr(application, f'transect_{i+1}_longitude', None)
        
        if lat_field and lng_field:
            latitude = float(lat_field)
            longitude = float(lng_field)
        else:
            latitude = field_latitude
            longitude = field_longitude
            
        transect_data.append({
            'index': i,
            'code': code,
            'latitude': latitude,
            'longitude': longitude
        })
    
    return render(request, 'grower_portal/grower/application_step5.html', {
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
