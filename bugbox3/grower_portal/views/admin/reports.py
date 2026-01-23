from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render

from bugbox3.core.permissions import IS_GROWERADMIN

from ...middleware import get_user_timezone
from ...models import GrowerReport


@login_required
@permission_required(IS_GROWERADMIN, raise_exception=True)
def report_list(request):
    reports_queryset = GrowerReport.objects.select_related(
        'application', 'application__grower', 'application__field',
        'application__field__farm', 'generated_by'
    ).order_by('-generated_at')

    paginator = Paginator(reports_queryset, 20)
    page_number = request.GET.get('page')
    reports = paginator.get_page(page_number)

    context = {
        'reports': reports,
        'user_timezone': get_user_timezone(request)
    }

    return render(request, 'grower_portal/admin/report_list.html', context)


@login_required
@permission_required(IS_GROWERADMIN, raise_exception=True)
def report_detail(request, report_id):
    report = get_object_or_404(
        GrowerReport.objects.select_related(
            'application', 'application__grower', 'application__field',
            'application__field__farm', 'generated_by'
        ),
        id=report_id
    )

    context = {
        'report': report,
        'user_timezone': get_user_timezone(request)
    }

    return render(request, 'grower_portal/admin/report_detail.html', context)
