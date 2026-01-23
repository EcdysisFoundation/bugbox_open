from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from bugbox3.core.permissions import IS_GROWERADMIN

from ...forms.admin.forms import TransectCodeFilterForm, TransectCodeGenerationForm
from ...middleware import get_user_timezone
from ...models import TransectCode


@login_required
@permission_required(IS_GROWERADMIN, raise_exception=True)
def transect_code_list(request):
    codes_queryset = TransectCode.objects.select_related(
        'created_by', 'used_in_application'
    ).order_by('-created_at')

    form = TransectCodeFilterForm(request.GET)

    if form.is_valid():
        search = form.cleaned_data.get('search')
        status = form.cleaned_data.get('status')
        usage = form.cleaned_data.get('usage')

        if search:
            codes_queryset = codes_queryset.filter(transect_code__icontains=search)

        if status == 'active':
            codes_queryset = codes_queryset.filter(is_active=True)
        elif status == 'inactive':
            codes_queryset = codes_queryset.filter(is_active=False)

        if usage == 'used':
            codes_queryset = codes_queryset.filter(is_used=True)
        elif usage == 'unused':
            codes_queryset = codes_queryset.filter(is_used=False)

    paginator = Paginator(codes_queryset, 20)
    page_number = request.GET.get('page')
    codes = paginator.get_page(page_number)

    context = {
        'codes': codes,
        'form': form,
        'user_timezone': get_user_timezone(request)
    }

    return render(request, 'grower_portal/admin/transect_code_list.html', context)


def _get_next_numeric_code():
    last_code = TransectCode.objects.select_for_update().order_by('-id').first()

    if not last_code:
        return 0

    code_str = last_code.transect_code
    if '-' in code_str:
        code_str = code_str.split('-')[-1]

    try:
        return int(code_str) + 1
    except (ValueError, TypeError):
        return 0


def _format_numeric_code(number):
    if number < 100000:
        return f"{number:05d}"
    elif number < 1000000:
        return f"{number:06d}"
    elif number < 10000000:
        return f"{number:07d}"
    elif number < 100000000:
        return f"{number:08d}"
    else:
        return str(number)


@login_required
@permission_required(IS_GROWERADMIN, raise_exception=True)
def transect_code_generate(request):
    generated_codes = []

    if request.method == 'POST':
        form = TransectCodeGenerationForm(request.POST)
        if form.is_valid():
            count = form.cleaned_data['count']
            prefix = form.cleaned_data.get('prefix', '').strip()

            try:
                with transaction.atomic():
                    start_number = _get_next_numeric_code()

                    for i in range(count):
                        number = start_number + i
                        numeric_code = _format_numeric_code(number)

                        if prefix:
                            full_code = f"{prefix}-{numeric_code}"
                        else:
                            full_code = numeric_code

                        TransectCode.objects.create(
                            transect_code=full_code,
                            is_active=True,
                            created_by=request.user
                        )
                        generated_codes.append(full_code)

                messages.success(
                    request,
                    f'Successfully generated {len(generated_codes)} transect code(s).'
                )

            except Exception as e:
                messages.error(request, f'Error generating codes: {str(e)}')
                generated_codes = []
    else:
        form = TransectCodeGenerationForm()

    context = {
        'form': form,
        'generated_codes': generated_codes,
        'user_timezone': get_user_timezone(request)
    }

    return render(request, 'grower_portal/admin/transect_code_generate.html', context)


@login_required
@permission_required(IS_GROWERADMIN, raise_exception=True)
def transect_code_deactivate(request, code_id):
    code = get_object_or_404(TransectCode, id=code_id)

    if request.method == 'POST':
        if code.is_used:
            messages.error(request, f'Cannot deactivate code {code.transect_code} - it is already in use.')
        else:
            code.is_active = False
            code.save()
            messages.success(request, f'Transect code {code.transect_code} has been deactivated.')

        return redirect('grower_portal:admin_transect_code_list')

    context = {
        'code': code,
        'user_timezone': get_user_timezone(request)
    }

    return render(request, 'grower_portal/admin/transect_code_deactivate.html', context)


@login_required
@permission_required(IS_GROWERADMIN, raise_exception=True)
def transect_code_reactivate(request, code_id):
    code = get_object_or_404(TransectCode, id=code_id)

    if request.method == 'POST':
        code.is_active = True
        code.save()
        messages.success(request, f'Transect code {code.transect_code} has been reactivated.')
        return redirect('grower_portal:admin_transect_code_list')

    context = {
        'code': code,
        'user_timezone': get_user_timezone(request)
    }

    return render(request, 'grower_portal/admin/transect_code_reactivate.html', context)
