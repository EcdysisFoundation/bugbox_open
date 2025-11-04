from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.contrib.auth.models import Permission

from bugbox3.core.permissions import IS_GROWER_USER, IS_GROWER
from ...models import GrowerProfile, GrowerApplication
from ...forms.grower.forms import GrowerProfileCompletionForm
from ...middleware import get_user_timezone


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
@permission_required(IS_GROWER_USER, raise_exception=True)
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

