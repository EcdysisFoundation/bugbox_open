from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, render

from bugbox3.core.permissions import IS_GROWERADMIN

from ...forms.admin.forms import FarmFilterForm
from ...middleware import get_user_timezone
from ...models import Farm


@login_required
@permission_required(IS_GROWERADMIN, raise_exception=True)
def farm_list(request):
    farms_queryset = Farm.objects.select_related('grower').annotate(
        field_count=Count('fields')
    ).order_by('-created_at')

    form = FarmFilterForm(request.GET)

    if form.is_valid():
        search = form.cleaned_data.get('search')
        grower = form.cleaned_data.get('grower')

        if search:
            farms_queryset = farms_queryset.filter(name__icontains=search)

        if grower:
            farms_queryset = farms_queryset.filter(grower=grower)

    paginator = Paginator(farms_queryset, 20)
    page_number = request.GET.get('page')
    farms = paginator.get_page(page_number)

    context = {
        'farms': farms,
        'form': form,
        'user_timezone': get_user_timezone(request)
    }

    return render(request, 'grower_portal/admin/farm_list.html', context)


@login_required
@permission_required(IS_GROWERADMIN, raise_exception=True)
def submittal_forms(request):
    return render(request, 'grower_portal/admin/')


@login_required
@permission_required(IS_GROWERADMIN, raise_exception=True)
def farm_detail(request, farm_id):
    farm = get_object_or_404(
        Farm.objects.select_related('grower').prefetch_related('fields'),
        id=farm_id
    )

    fields = farm.fields.all()

    context = {
        'farm': farm,
        'fields': fields,
        'user_timezone': get_user_timezone(request)
    }

    return render(request, 'grower_portal/admin/farm_detail.html', context)
