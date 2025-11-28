from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db.models import Q

from bugbox3.core.permissions import IS_GROWERADMIN
from ...models import GrowerProfile, Farm, Field, GrowerApplication
from ...forms.admin.forms import GrowerFilterForm
from ...middleware import get_user_timezone

User = get_user_model()


@login_required
@permission_required(IS_GROWERADMIN, raise_exception=True)
def grower_list(request):
    growers_queryset = GrowerProfile.objects.select_related('user').order_by('-created_at')
    
    form = GrowerFilterForm(request.GET)
    
    if form.is_valid():
        search = form.cleaned_data.get('search')
        profile_completed = form.cleaned_data.get('profile_completed')
        
        if search:
            growers_queryset = growers_queryset.filter(
                Q(user__name__icontains=search) |
                Q(user__email__icontains=search)
            )
        
        if profile_completed == 'completed':
            growers_queryset = growers_queryset.filter(profile_completed=True)
        elif profile_completed == 'incomplete':
            growers_queryset = growers_queryset.filter(profile_completed=False)
    
    paginator = Paginator(growers_queryset, 20)
    page_number = request.GET.get('page')
    growers = paginator.get_page(page_number)
    
    context = {
        'growers': growers,
        'form': form,
        'user_timezone': get_user_timezone(request)
    }
    
    return render(request, 'grower_portal/admin/grower_list.html', context)


@login_required
@permission_required(IS_GROWERADMIN, raise_exception=True)
def grower_detail(request, grower_id):
    user = get_object_or_404(User, id=grower_id)
    
    try:
        grower_profile = user.grower_profile
    except GrowerProfile.DoesNotExist:
        grower_profile = None
    
    farms = Farm.objects.filter(grower=user).prefetch_related('fields')
    fields = Field.objects.filter(farm__grower=user).select_related('farm')
    applications = GrowerApplication.objects.filter(grower=user).select_related(
        'field', 'field__farm'
    ).order_by('-date_sampled')
    
    context = {
        'grower': user,
        'grower_profile': grower_profile,
        'farms': farms,
        'fields': fields,
        'applications': applications,
        'user_timezone': get_user_timezone(request)
    }
    
    return render(request, 'grower_portal/admin/grower_detail.html', context)
