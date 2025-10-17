from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.http import Http404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.contrib.auth import get_user_model
from django.forms import modelformset_factory
from django.db import IntegrityError, transaction

from bugbox3.core.permissions import IS_GROWER_USER, IS_GROWER
from ...models import (
    GrowerProfile, Farm, Field, GrowerApplication, ApplicationMeasurement,
    ManagementPractices, GrazingEvent
)
from ...forms.grower.forms import (
    GrowerProfileCompletionForm, ApplicationCreationForm,
    ManagementPracticesForm, ApplicationMeasurementForm, GrazingEventForm
)

User = get_user_model()


@login_required
@permission_required(IS_GROWER_USER, raise_exception=True)
def profile_complete(request):
    """
    One-time profile completion form for new growers.
    This view is only shown if the grower hasn't completed their profile yet.
    """
    # Check if profile already exists and is completed
    try:
        grower_profile = request.user.grower_profile
        if grower_profile.profile_completed:
            return redirect('grower_portal:dashboard')
    except GrowerProfile.DoesNotExist:
        pass

    if request.method == 'POST':
        action = request.POST.get('action', 'complete')
        
        if action == 'skip':
            # Create a minimal profile and mark as completed
            grower_profile, created = GrowerProfile.objects.get_or_create(
                user=request.user,
                defaults={'profile_completed': True}
            )
            if not created:
                grower_profile.profile_completed = True
                grower_profile.save()
            
            messages.info(request, 'Profile completion skipped. You can complete it later from your dashboard.')
            return redirect('grower_portal:dashboard')
        
        else:  # action == 'complete'
            form = GrowerProfileCompletionForm(request.POST)
            if form.is_valid():
                # Create or update the grower profile
                grower_profile, created = GrowerProfile.objects.get_or_create(
                    user=request.user,
                    defaults=form.cleaned_data
                )
                if not created:
                    # Update existing profile
                    for field, value in form.cleaned_data.items():
                        setattr(grower_profile, field, value)
                
                grower_profile.profile_completed = True
                grower_profile.save()
                
                messages.success(request, 'Your grower profile has been completed successfully!')
                return redirect('grower_portal:dashboard')
    else:
        form = GrowerProfileCompletionForm()

    return render(request, 'grower_portal/grower/profile_complete.html', {
        'form': form
    })


@login_required
@permission_required(IS_GROWER, raise_exception=True)
def dashboard(request):
    """
    Main grower dashboard showing applications and quick actions.
    """
    try:
        grower_profile = request.user.grower_profile
    except GrowerProfile.DoesNotExist:
        # If no profile exists, redirect to profile completion
        return redirect('grower_portal:profile_complete')
    
    if not grower_profile.profile_completed:
        return redirect('grower_portal:profile_complete')
    
    applications = GrowerApplication.objects.filter(grower=request.user).order_by('-date_sampled')
    
    return render(request, 'grower_portal/grower/dashboard.html', {
        'grower_profile': grower_profile,
        'applications': applications
    })


@login_required
@permission_required(IS_GROWER, raise_exception=True)
def profile_edit(request):
    """
    Edit grower profile information.
    """
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
        'is_edit': True
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
                            crop_variety=form.cleaned_data.get('crop_variety', ''),
                            forage_varieties=form.cleaned_data.get('forage_varieties', ''),
                            paddock_size=form.cleaned_data.get('paddock_size', ''),
                            rootstock_species=form.cleaned_data.get('rootstock_species', ''),
                            transitional_status=form.cleaned_data.get('transitional_status', '')
                        )
                    
                    application = GrowerApplication.objects.create(
                        field=field,
                        grower=request.user,
                        date_sampled=form.cleaned_data['date_sampled'],
                        transect_code_1=form.cleaned_data.get('transect_code_1'),
                        transect_code_2=form.cleaned_data.get('transect_code_2'),
                        transect_code_3=form.cleaned_data.get('transect_code_3'),
                        transect_code_4=form.cleaned_data.get('transect_code_4')
                    )
                    
                    for i, code in enumerate(application.transect_codes, 1):
                        ApplicationMeasurement.objects.create(
                            application=application,
                            transect_number=i
                        )
                    
                    messages.success(request, f'Application {application.submission_code} created successfully!')
                    return redirect('grower_portal:application_step1', application_id=application.id)
                    
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
        'form': form
    })


@login_required
@permission_required(IS_GROWER, raise_exception=True)
def application_step1(request, application_id):
    application = get_object_or_404(
        GrowerApplication,
        id=application_id,
        grower=request.user
    )
    
    return render(request, 'grower_portal/grower/application_step1.html', {
        'application': application
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
        'form': form
    })


@login_required
@permission_required(IS_GROWER, raise_exception=True)
def application_step3(request, application_id):
    application = get_object_or_404(
        GrowerApplication,
        id=application_id,
        grower=request.user
    )
    
    measurements = ApplicationMeasurement.objects.filter(application=application).order_by('transect_number')
    MeasurementFormSet = modelformset_factory(
        ApplicationMeasurement,
        form=ApplicationMeasurementForm,
        extra=0,
        can_delete=False
    )
    
    if request.method == 'POST':
        formset = MeasurementFormSet(request.POST, queryset=measurements)
        if formset.is_valid():
            formset.save()
            messages.success(request, 'Transect measurements saved successfully!')
            
            if application.field.field_type == 'range':
                return redirect('grower_portal:application_step4', application_id=application.id)
            else:
                return redirect('grower_portal:application_step5', application_id=application.id)
    else:
        formset = MeasurementFormSet(queryset=measurements)
    
    for form, transect_code in zip(formset.forms, application.transect_codes):
        form.transect_code = transect_code
        for field_name, field in form.fields.items():
            if field_name not in ['supports_dairy', 'is_confined_dairy']:
                attrs = {'class': 'form-control'}
                if field_name in ['acres_sampled', 'years_under_management']:
                    attrs['required'] = 'required'
                field.widget.attrs.update(attrs)
            else:
                field.widget.attrs.update({'class': 'form-check-input'})
    
    return render(request, 'grower_portal/grower/application_step3.html', {
        'application': application,
        'formset': formset
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
    
    measurements = ApplicationMeasurement.objects.filter(application=application).order_by('transect_number')
    
    grazing_events = []
    for measurement in measurements:
        events = GrazingEvent.objects.filter(application_measurement=measurement).order_by('event_number')
        grazing_events.extend(events)
    
    GrazingEventFormSet = modelformset_factory(
        GrazingEvent,
        form=GrazingEventForm,
        extra=max(0, 4 - len(grazing_events)),
        max_num=4,
        can_delete=True
    )
    
    if request.method == 'POST':
        formset = GrazingEventFormSet(request.POST, queryset=GrazingEvent.objects.filter(application_measurement__application=application))
        if formset.is_valid():
            instances = formset.save(commit=False)
            for i, instance in enumerate(instances, 1):
                if not instance.application_measurement_id:
                    instance.application_measurement = measurements.first()
                instance.event_number = i
                instance.save()
            for obj in formset.deleted_objects:
                obj.delete()
            messages.success(request, 'Grazing events saved successfully!')
            return redirect('grower_portal:application_step5', application_id=application.id)
    else:
        formset = GrazingEventFormSet(queryset=GrazingEvent.objects.filter(application_measurement__application=application))
    
    for form in formset.forms:
        for field_name, field in form.fields.items():
            if field_name not in ['DELETE']:
                field.widget.attrs.update({'class': 'form-control'})
    
    return render(request, 'grower_portal/grower/application_step4.html', {
        'application': application,
        'formset': formset
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
    
    measurements = ApplicationMeasurement.objects.filter(application=application).order_by('transect_number')
    grazing_events = GrazingEvent.objects.filter(application_measurement__application=application).order_by('event_number') if application.field.field_type == 'range' else []
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'submit':
            application.is_submitted = True
            application.is_draft = False
            application.save()
            messages.success(request, f'Application {application.submission_code} submitted successfully!')
            return redirect('grower_portal:dashboard')
        elif action == 'save_draft':
            application.is_draft = True
            application.save()
            messages.success(request, f'Application {application.submission_code} saved as draft.')
            return redirect('grower_portal:dashboard')
    
    return render(request, 'grower_portal/grower/application_step5.html', {
        'application': application,
        'management_practices': management_practices,
        'measurements': measurements,
        'grazing_events': grazing_events
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
    
    measurements = ApplicationMeasurement.objects.filter(application=application).order_by('transect_number')
    grazing_events = GrazingEvent.objects.filter(application_measurement__application=application).order_by('event_number') if application.field.field_type == 'range' else []
    
    return render(request, 'grower_portal/grower/application_view.html', {
        'application': application,
        'management_practices': management_practices,
        'measurements': measurements,
        'grazing_events': grazing_events
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
        'application': application
    })
