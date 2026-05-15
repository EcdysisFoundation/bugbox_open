from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from bugbox3.core.permissions import IS_GROWERADMIN

from ...forms.admin.application_forms import LinkGrowerForm
from ...forms.admin.forms import ApplicationFilterForm
from ...middleware import get_user_timezone
from ...models import GrazingEvent, GrowerApplication, ManagementPractices, TransectMeasurement
from ...utils import get_grower_maps_json_context

User = get_user_model()


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
        linked_status = form.cleaned_data.get('linked_status')
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
                Q(grower_name__icontains=search) |
                Q(grower_email__icontains=search) |
                Q(field__farm__name__icontains=search) |
                Q(field__field_name__icontains=search)
            )

        if status == 'draft':
            applications_queryset = applications_queryset.filter(is_draft=True)
        elif status == 'submitted':
            applications_queryset = applications_queryset.filter(is_submitted=True)

        if field_type:
            applications_queryset = applications_queryset.filter(field__field_type=field_type)

        if linked_status == 'linked':
            applications_queryset = applications_queryset.filter(grower__isnull=False)
        elif linked_status == 'unlinked':
            applications_queryset = applications_queryset.filter(grower__isnull=True)

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

    transect_measurements = TransectMeasurement.objects.filter(
        application=application
    ).prefetch_related(
        'drop_plate',
        'vegetation',
        'soil',
        'compaction',
        'infiltrometer',
        'infiltration_ring',
    ).order_by('transect_index')

    map_transect_points = []
    for i, code in enumerate(application.transect_codes):
        location = getattr(application, f'transect_{i + 1}_location', None)
        if location:
            map_transect_points.append({
                'index': i,
                'code': code,
                'latitude': float(location.y),
                'longitude': float(location.x),
            })
    context = {
        'application': application,
        'management_practices': management_practices,
        'grazing_events': grazing_events,
        'transect_measurements': transect_measurements,
        'user_timezone': get_user_timezone(request),
    }
    if application.field:
        context['json_context'] = get_grower_maps_json_context(map_transect_points)

    return render(request, 'grower_portal/admin/application_detail.html', context)


@login_required
@permission_required(IS_GROWERADMIN, raise_exception=True)
def application_edit_redirect(request, application_id):
    application = get_object_or_404(GrowerApplication, id=application_id)
    if not application.is_draft:
        messages.error(request, 'Only draft applications can be edited through the wizard.')
        return redirect('grower_portal:admin_application_detail', application_id=application.id)
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


@login_required
@permission_required(IS_GROWERADMIN, raise_exception=True)
def link_application_to_grower(request, application_id):
    """Link an unlinked application to a grower account"""
    application = get_object_or_404(GrowerApplication, id=application_id)

    if application.grower:
        messages.warning(
            request, f'Application {
                application.submission_code} is already linked to grower {
                application.grower.email}.')
        return redirect('grower_portal:admin_application_detail', application_id=application.id)

    search_results = None

    if request.method == 'POST':
        form = LinkGrowerForm(request.POST)

        if 'search' in request.POST:
            search_term = request.POST.get('grower_search', '').strip()
            if search_term:
                search_results = User.objects.filter(
                    groups__name='is_grower'
                ).filter(
                    Q(name__icontains=search_term) | Q(email__icontains=search_term)
                ).distinct()[:20]

                if not search_results:
                    messages.info(request, f'No growers found matching "{search_term}".')
                else:
                    messages.success(request, f'Found {search_results.count()} grower(s) matching "{search_term}".')

                form = LinkGrowerForm(initial={'grower_search': search_term})
            else:
                messages.error(request, 'Please enter a search term.')
                form = LinkGrowerForm(request.POST)

        elif 'link' in request.POST:
            grower_email = request.POST.get('grower_email', '').strip()
            selected_grower_id = request.POST.get('selected_grower_id', '').strip()

            if not grower_email and not selected_grower_id:
                messages.error(request, 'Please either enter a grower email or select a grower from search results.')
            else:
                try:
                    with transaction.atomic():
                        grower = None

                        if grower_email:
                            try:
                                grower = User.objects.get(
                                    email=grower_email,
                                    groups__name='is_grower'
                                )
                            except User.DoesNotExist:
                                messages.error(request, f'No grower found with email "{grower_email}".')
                                form = LinkGrowerForm(request.POST)
                                context = {
                                    'application': application,
                                    'form': form,
                                    'search_results': search_results,
                                    'user_timezone': get_user_timezone(request)
                                }
                                return render(request, 'grower_portal/admin/application_link_grower.html', context)

                        elif selected_grower_id:
                            try:
                                grower = User.objects.get(
                                    id=int(selected_grower_id),
                                    groups__name='is_grower'
                                )
                            except (User.DoesNotExist, ValueError):
                                messages.error(request, 'Selected grower not found or invalid.')
                                form = LinkGrowerForm(request.POST)
                                context = {
                                    'application': application,
                                    'form': form,
                                    'search_results': search_results,
                                    'user_timezone': get_user_timezone(request)
                                }
                                return render(request, 'grower_portal/admin/application_link_grower.html', context)

                        if grower:
                            application.grower = grower
                            application.save()

                            if application.field and application.field.farm:
                                farm = application.field.farm
                                if not farm.grower:
                                    farm.grower = grower
                                    farm.save()

                            messages.success(
                                request,
                                f'Application {application.submission_code} has been linked to grower {grower.email}.'
                            )
                            return redirect('grower_portal:admin_application_detail', application_id=application.id)

                except Exception as e:
                    messages.error(request, f'Error linking application: {str(e)}')
    else:
        initial_data = {}
        if application.grower_email and application.grower_email != 'No email':
            initial_data['grower_email'] = application.grower_email
        form = LinkGrowerForm(initial=initial_data)

    context = {
        'application': application,
        'form': form,
        'search_results': search_results,
        'user_timezone': get_user_timezone(request)
    }

    return render(request, 'grower_portal/admin/application_link_grower.html', context)
