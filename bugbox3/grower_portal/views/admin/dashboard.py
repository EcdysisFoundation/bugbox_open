from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render

from bugbox3.core.permissions import IS_GROWERADMIN

from ...middleware import get_user_timezone
from ...models import Farm, Field, GrowerApplication, GrowerProfile

User = get_user_model()


@login_required
@permission_required(IS_GROWERADMIN, raise_exception=True)
def admin_dashboard(request):
    total_growers = GrowerProfile.objects.count()
    total_farms = Farm.objects.count()
    total_fields = Field.objects.count()
    total_applications = GrowerApplication.objects.count()

    submitted_applications = GrowerApplication.objects.filter(is_submitted=True).count()
    draft_applications = GrowerApplication.objects.filter(is_draft=True).count()

    recent_applications = GrowerApplication.objects.select_related(
        'grower', 'field', 'field__farm'
    ).order_by('-date_sampled', '-created_at')[:10]

    context = {
        'total_growers': total_growers,
        'total_farms': total_farms,
        'total_fields': total_fields,
        'total_applications': total_applications,
        'submitted_applications': submitted_applications,
        'draft_applications': draft_applications,
        'recent_applications': recent_applications,
        'user_timezone': get_user_timezone(request)
    }

    return render(request, 'grower_portal/admin/dashboard.html', context)
