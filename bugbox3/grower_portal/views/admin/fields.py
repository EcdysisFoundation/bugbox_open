from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render

from bugbox3.core.permissions import IS_GROWERADMIN

from ...forms.admin.forms import FieldFilterForm
from ...middleware import get_user_timezone
from ...models import Field, GrowerApplication, ManagementPractices


@login_required
@permission_required(IS_GROWERADMIN, raise_exception=True)
def field_list(request):
    fields_queryset = Field.objects.select_related('farm', 'farm__grower').order_by('-created_at')

    form = FieldFilterForm(request.GET)

    if form.is_valid():
        search = form.cleaned_data.get('search')
        field_type = form.cleaned_data.get('field_type')
        grower = form.cleaned_data.get('grower')
        farm = form.cleaned_data.get('farm')

        if search:
            fields_queryset = fields_queryset.filter(field_name__icontains=search)

        if field_type:
            fields_queryset = fields_queryset.filter(field_type=field_type)

        if grower:
            fields_queryset = fields_queryset.filter(farm__grower=grower)

        if farm:
            fields_queryset = fields_queryset.filter(farm=farm)

    paginator = Paginator(fields_queryset, 20)
    page_number = request.GET.get('page')
    fields = paginator.get_page(page_number)

    context = {
        'fields': fields,
        'form': form,
        'user_timezone': get_user_timezone(request)
    }

    return render(request, 'grower_portal/admin/field_list.html', context)


@login_required
@permission_required(IS_GROWERADMIN, raise_exception=True)
def field_detail(request, field_id):
    field = get_object_or_404(
        Field.objects.select_related('farm', 'farm__grower'),
        id=field_id
    )

    applications = GrowerApplication.objects.filter(field=field).order_by('-date_sampled')

    management_practices = None
    if applications.exists():
        latest_application = applications.first()
        try:
            management_practices = ManagementPractices.objects.get(application=latest_application)
        except ManagementPractices.DoesNotExist:
            pass

    context = {
        'field': field,
        'management_practices': management_practices,
        'applications': applications,
        'user_timezone': get_user_timezone(request)
    }

    return render(request, 'grower_portal/admin/field_detail.html', context)
