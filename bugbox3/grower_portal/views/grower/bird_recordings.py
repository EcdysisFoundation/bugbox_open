import json

from django.contrib.auth.decorators import login_required, permission_required
from django.core.cache import cache
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST

from bugbox3.core.permissions import IS_GROWER
from bugbox3.libs.utilities import get_json_context

from ...constants import BIRD_RECORDING_MAX_BYTES, BIRD_RECORDING_MAX_BYTES_PER_CODE
from ...middleware import get_user_timezone
from ...models import BirdRecordingUpload
from ...services.bird_recording_upload import (
    BirdRecordingValidationError,
    complete_upload,
    create_presigned_put,
    initiate_upload,
    s3_configured,
    quota_for_code,
    validate_sample_code_for_upload,
)

_RATE_LIMIT_INITIATE = 30  # per hour per user
_RATE_LIMIT_WINDOW = 3600


def _parse_json_body(request) -> dict:
    if not request.body:
        return {}
    try:
        return json.loads(request.body.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return {}


def _json_error(message: str, status: int = 400) -> JsonResponse:
    return JsonResponse({'ok': False, 'error': message}, status=status)


def _rate_limit_or_response(user_id: int, action: str, limit: int) -> JsonResponse | None:
    key = f'bird_recording_rl:{action}:{user_id}'
    count = cache.get(key, 0)
    if count >= limit:
        return _json_error('Too many upload attempts. Please wait and try again later.', status=429)
    if count == 0:
        cache.set(key, 1, _RATE_LIMIT_WINDOW)
    else:
        cache.incr(key)
    return None


@login_required
@permission_required(IS_GROWER, raise_exception=True)
@require_GET
def bird_recording_upload_page(request):
    max_mb = BIRD_RECORDING_MAX_BYTES // (1024 * 1024)
    max_per_code_gb = BIRD_RECORDING_MAX_BYTES_PER_CODE // (1024 * 1024 * 1024)
    ctx = {
        'user_timezone': get_user_timezone(request),
        's3_available': s3_configured(),
        'max_file_mb': max_mb,
        'max_per_code_gb': max_per_code_gb,
        'json_context': get_json_context({
            'validateCodeUrl': reverse('grower_portal:bird_recording_validate_code'),
            'initiateUrl': reverse('grower_portal:bird_recording_initiate'),
            'completeUrl': reverse('grower_portal:bird_recording_complete'),
            'listUrl': reverse('grower_portal:bird_recording_list'),
            'maxFileBytes': BIRD_RECORDING_MAX_BYTES,
            'maxBytesPerCode': BIRD_RECORDING_MAX_BYTES_PER_CODE,
            'csrfToken': get_token(request),
        }),
    }
    return render(request, 'grower_portal/grower/bird_recording_upload.html', ctx)


@login_required
@permission_required(IS_GROWER, raise_exception=True)
@require_GET
def bird_recording_list(request):
    uploads = (
        BirdRecordingUpload.objects.filter(
            grower=request.user,
            status=BirdRecordingUpload.STATUS_COMPLETED,
        )
        .select_related('sample_code')
        .order_by('-uploaded_at')[:100]
    )
    return render(request, 'grower_portal/grower/bird_recording_list.html', {
        'uploads': uploads,
        'user_timezone': get_user_timezone(request),
        's3_available': s3_configured(),
    })


@login_required
@permission_required(IS_GROWER, raise_exception=True)
@require_POST
def bird_recording_validate_code(request):
    data = _parse_json_body(request)
    code = data.get('sample_code', request.POST.get('sample_code', ''))
    try:
        validated = validate_sample_code_for_upload(request.user, code)
    except BirdRecordingValidationError as exc:
        return _json_error(exc.message)

    sc = validated.sample_code
    quota = quota_for_code(request.user, sc)
    return JsonResponse({
        'ok': True,
        'sample_code': sc.code,
        'year_sampled': validated.year_sampled,
        'project_type': sc.project_type,
        **quota,
    })


@login_required
@permission_required(IS_GROWER, raise_exception=True)
@require_POST
def bird_recording_initiate(request):
    limited = _rate_limit_or_response(request.user.id, 'initiate', _RATE_LIMIT_INITIATE)
    if limited:
        return limited

    data = _parse_json_body(request)
    code = data.get('sample_code', '')
    filename = data.get('filename', '')
    content_type = data.get('content_type', '')
    try:
        file_size = int(data.get('file_size', 0))
    except (TypeError, ValueError):
        return _json_error('Invalid file size.')

    try:
        record = initiate_upload(request.user, code, filename, content_type, file_size)
        presigned = create_presigned_put(record.s3_key, record.content_type, record.file_size_bytes)
    except BirdRecordingValidationError as exc:
        return _json_error(exc.message)

    return JsonResponse({
        'ok': True,
        'upload_id': record.id,
        **presigned,
    })


@login_required
@permission_required(IS_GROWER, raise_exception=True)
@require_POST
def bird_recording_complete(request):
    limited = _rate_limit_or_response(request.user.id, 'complete', _RATE_LIMIT_INITIATE)
    if limited:
        return limited

    data = _parse_json_body(request)
    try:
        upload_id = int(data.get('upload_id', 0))
    except (TypeError, ValueError):
        return _json_error('Invalid upload id.')

    try:
        record = complete_upload(request.user, upload_id)
    except BirdRecordingValidationError as exc:
        return _json_error(exc.message)

    return JsonResponse({
        'ok': True,
        'upload_id': record.id,
        'sample_code': record.sample_code.code,
        'original_filename': record.original_filename,
        'file_size_bytes': record.file_size_bytes,
        'uploaded_at': record.uploaded_at.isoformat() if record.uploaded_at else None,
    })
