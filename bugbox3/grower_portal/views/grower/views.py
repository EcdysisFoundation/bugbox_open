from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.http import Http404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.contrib.auth import get_user_model

from bugbox3.core.permissions import IS_GROWER_USER, IS_GROWER
from ...models import GrowerProfile
from ...forms.grower.forms import GrowerProfileCompletionForm

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
    
    # Check if profile is completed
    if not grower_profile.profile_completed:
        return redirect('grower_portal:profile_complete')
    
    # TODO: Add actual applications when the models are implemented
    # For now, we'll show empty state
    applications = []
    
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
