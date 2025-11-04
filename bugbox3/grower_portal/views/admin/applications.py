from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q

from bugbox3.core.permissions import IS_GROWERADMIN
from ...models import GrowerApplication, ManagementPractices, GrazingEvent
from ...forms.admin.forms import ApplicationFilterForm
from ...middleware import get_user_timezone


@login_required
@permission_required(IS_GROWERADMIN, raise_exception=True)
def application_list(request):
    applications_queryset = GrowerApplication.objects.select_related(
        'grower', 'field', 'field__farm'
    ).order_by('-date_sampled', '-created_at')
    
    form = ApplicationFilterForm(request.GET)
    
    if form.is_valid():
        search = form.cleaned_data.get('search')
        status = form.cleaned_data.get('status')
        field_type = form.cleaned_data.get('field_type')
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')
        
        if search:
            applications_queryset = applications_queryset.filter(
                Q(submission_code__icontains=search) |
                Q(transect_code_1__icontains=search) |
                Q(transect_code_2__icontains=search) |
                Q(transect_code_3__icontains=search) |
                Q(transect_code_4__icontains=search) |
                Q(grower__name__icontains=search) |
                Q(grower__email__icontains=search) |
                Q(field__farm__name__icontains=search) |
                Q(field__field_name__icontains=search)
            )
        
        if status == 'draft':
            applications_queryset = applications_queryset.filter(is_draft=True)
        elif status == 'submitted':
            applications_queryset = applications_queryset.filter(is_submitted=True)
        
        if field_type:
            applications_queryset = applications_queryset.filter(field__field_type=field_type)
        
        if date_from:
            applications_queryset = applications_queryset.filter(date_sampled__gte=date_from)
        
        if date_to:
            applications_queryset = applications_queryset.filter(date_sampled__lte=date_to)
    
    paginator = Paginator(applications_queryset, 20)
    page_number = request.GET.get('page')
    applications = paginator.get_page(page_number)
    
    context = {
        'applications': applications,
        'form': form,
        'user_timezone': get_user_timezone(request)
    }
    
    return render(request, 'grower_portal/admin/application_list.html', context)


@login_required
@permission_required(IS_GROWERADMIN, raise_exception=True)
def application_detail(request, application_id):
    application = get_object_or_404(
        GrowerApplication.objects.select_related('grower', 'field', 'field__farm'),
        id=application_id
    )
    
    try:
        management_practices = ManagementPractices.objects.get(application=application)
    except ManagementPractices.DoesNotExist:
        management_practices = None
    
    grazing_events = GrazingEvent.objects.filter(
        application=application
    ).prefetch_related('animals').order_by('event_number')
    
    transect_data = []
    for i in range(1, 5):
        code = getattr(application, f'transect_code_{i}', None)
        location = getattr(application, f'transect_{i}_location', None)
        if code:
            lat = location.y if location else None
            lon = location.x if location else None
            transect_data.append({
                'number': i,
                'code': code,
                'latitude': lat,
                'longitude': lon
            })
    
    context = {
        'application': application,
        'management_practices': management_practices,
        'grazing_events': grazing_events,
        'transect_data': transect_data,
        'user_timezone': get_user_timezone(request)
    }
    
    return render(request, 'grower_portal/admin/application_detail.html', context)


@login_required
@permission_required(IS_GROWERADMIN, raise_exception=True)
def application_edit_redirect(request, application_id):
    application = get_object_or_404(GrowerApplication, id=application_id)
    return redirect('grower_portal:admin_application_edit_basic', application_id=application.id)


@login_required
@permission_required(IS_GROWERADMIN, raise_exception=True)
def application_delete(request, application_id):
    application = get_object_or_404(GrowerApplication, id=application_id)
    
    has_reports = application.reports.exists()
    
    if request.method == 'POST':
        if has_reports:
            messages.error(
                request,
                f'Cannot delete application {application.submission_code} - it has associated reports. '
                'Please delete the reports first.'
            )
            return redirect('grower_portal:admin_application_detail', application_id=application.id)
        
        submission_code = application.submission_code
        application.delete()
        messages.success(request, f'Application {submission_code} has been deleted.')
        return redirect('grower_portal:admin_application_list')
    
    context = {
        'application': application,
        'has_reports': has_reports,
        'user_timezone': get_user_timezone(request)
    }
    
    return render(request, 'grower_portal/admin/application_delete.html', context)

