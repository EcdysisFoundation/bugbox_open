"""

Grower bird recording uploads: validate sample codes and presigned direct-to-S3 PUT.

"""



from __future__ import annotations



import re

import boto3

from dataclasses import dataclass

from datetime import datetime, timezone

from pathlib import Path

from uuid import uuid4

from botocore.exceptions import ClientError

from django.conf import settings

from django.db import transaction

from django.db.models import Sum

from django.utils import timezone as django_timezone

from django.core.files.storage import default_storage




from bugbox3.grower_portal.constants import (

    BIRD_RECORDING_ALLOWED_CONTENT_TYPES,

    BIRD_RECORDING_ALLOWED_EXTENSIONS,

    BIRD_RECORDING_MAX_BYTES,

    BIRD_RECORDING_MAX_BYTES_PER_CODE,

    BIRD_RECORDING_PRESIGNED_EXPIRY_SECONDS,

    GROWER_DATA_S3_PREFIX,

)

from bugbox3.grower_portal.models import BirdRecordingUpload, GrowerSampleCodeMapping, SampleCode





class BirdRecordingValidationError(Exception):

    """Raised when sample code or upload parameters are invalid."""



    def __init__(self, message: str):

        self.message = message

        super().__init__(message)





@dataclass

class ValidatedSampleCode:

    sample_code: SampleCode

    year_sampled: int





def _default_storage_is_s3() -> bool:




    return 's3storage' in default_storage.__class__.__name__.lower()





def get_media_s3_client():

    """Boto3 S3 client when default file storage is the media bucket (not module-import time)."""

    if not (

        settings.AWS_STORAGE_BUCKET_NAME_MEDIA

        and settings.AWS_ACCESS_KEY_ID

        and settings.AWS_SECRET_ACCESS_KEY

        and _default_storage_is_s3()

    ):

        return None




    return boto3.client(

        's3',

        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,

        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,

        region_name=settings.AWS_REGION,

    )





def s3_configured() -> bool:

    return get_media_s3_client() is not None





def build_recording_s3_key(year: int, sample_code_str: str, original_filename: str) -> str:

    """grower_portal_data/birds/recordings/{year}/{code}/{timestamp}_{uuid}_{name}"""

    base = Path(original_filename).name

    safe = re.sub(r'[^\w.\-]', '_', base).strip('._') or 'recording'

    safe = safe[:200]

    stamp = datetime.now(timezone.utc).strftime('%Y%m%d')

    uid = uuid4().hex[:8]

    return (

        f'{GROWER_DATA_S3_PREFIX}/birds/recordings/{year}/'

        f'{sample_code_str}/{stamp}_{uid}_{safe}'

    )





def resolve_year_sampled(user, sample_code: SampleCode) -> int:

    """Mapping year, then SampleCode.year, then current calendar year."""

    mapping = GrowerSampleCodeMapping.objects.filter(

        grower=user,

        sample_code=sample_code,

    ).first()

    if mapping is not None:

        return mapping.year_sampled

    if sample_code.year is not None:

        return sample_code.year

    return django_timezone.now().year





def bytes_used_for_code(grower, sample_code: SampleCode) -> int:

    """Sum of completed + pending upload sizes for this grower and code."""

    total = (

        BirdRecordingUpload.objects.filter(

            grower=grower,

            sample_code=sample_code,

            status__in=(

                BirdRecordingUpload.STATUS_COMPLETED,

                BirdRecordingUpload.STATUS_PENDING,

            ),

        ).aggregate(total=Sum('file_size_bytes'))['total']

    )

    return int(total or 0)





def quota_for_code(grower, sample_code: SampleCode) -> dict:

    used = bytes_used_for_code(grower, sample_code)

    limit = BIRD_RECORDING_MAX_BYTES_PER_CODE

    remaining = max(0, limit - used)

    return {

        'bytes_used': used,

        'bytes_limit': limit,

        'bytes_remaining': remaining,

    }





def validate_sample_code_for_upload(user, code: str) -> ValidatedSampleCode:

    code = (code or '').strip()

    if not code:

        raise BirdRecordingValidationError('Sample code is required.')



    try:

        sample_code = SampleCode.objects.get(code=code)

    except SampleCode.DoesNotExist:

        raise BirdRecordingValidationError(f'Sample code "{code}" was not found.')



    if not sample_code.is_active:

        raise BirdRecordingValidationError(f'Sample code "{code}" is not active.')



    year_sampled = resolve_year_sampled(user, sample_code)

    return ValidatedSampleCode(sample_code=sample_code, year_sampled=year_sampled)





# Backward-compatible alias

validate_grower_sample_code = validate_sample_code_for_upload





def validate_upload_file(filename: str, content_type: str, file_size: int) -> None:

    if file_size <= 0:

        raise BirdRecordingValidationError('File size must be greater than zero.')

    if file_size > BIRD_RECORDING_MAX_BYTES:

        max_mb = BIRD_RECORDING_MAX_BYTES // (1024 * 1024)

        raise BirdRecordingValidationError(f'File exceeds the maximum size of {max_mb} MB.')



    ext = Path(filename or '').suffix.lower()

    if ext and ext not in BIRD_RECORDING_ALLOWED_EXTENSIONS:

        allowed = ', '.join(sorted(BIRD_RECORDING_ALLOWED_EXTENSIONS))

        raise BirdRecordingValidationError(

            f'File type not allowed. Allowed extensions: {allowed}'

        )



    ct = (content_type or '').split(';')[0].strip().lower()

    if ct and ct not in BIRD_RECORDING_ALLOWED_CONTENT_TYPES:

        raise BirdRecordingValidationError(

            'File content type not allowed. Please upload WAV, MP3, or MP4.'

        )





def validate_code_quota(grower, sample_code: SampleCode, file_size: int) -> None:

    used = bytes_used_for_code(grower, sample_code)

    if used + file_size > BIRD_RECORDING_MAX_BYTES_PER_CODE:

        limit_gb = BIRD_RECORDING_MAX_BYTES_PER_CODE // (1024 * 1024 * 1024)

        used_mb = used // (1024 * 1024)

        remaining = max(0, BIRD_RECORDING_MAX_BYTES_PER_CODE - used)

        remaining_mb = remaining // (1024 * 1024)

        raise BirdRecordingValidationError(

            f'Total uploads for this sample code cannot exceed {limit_gb} GB '

            f'({used_mb} MB used, {remaining_mb} MB remaining).'

        )





def create_presigned_put(s3_key: str, content_type: str, file_size: int) -> dict:

    if not s3_configured():

        raise BirdRecordingValidationError(

            'Recording uploads are not available: cloud storage is not configured.'

        )



    client = get_media_s3_client()

    bucket = settings.AWS_STORAGE_BUCKET_NAME_MEDIA

    upload_url = client.generate_presigned_url(

        'put_object',

        Params={

            'Bucket': bucket,

            'Key': s3_key,

            'ContentType': content_type or 'application/octet-stream',

            'ContentLength': file_size,

        },

        ExpiresIn=BIRD_RECORDING_PRESIGNED_EXPIRY_SECONDS,

    )

    return {

        'upload_url': upload_url,

        'method': 'PUT',

        'bucket': bucket,

        's3_key': s3_key,

        'expires_in': BIRD_RECORDING_PRESIGNED_EXPIRY_SECONDS,

    }





def initiate_upload(user, code: str, filename: str, content_type: str, file_size: int) -> BirdRecordingUpload:

    validated = validate_sample_code_for_upload(user, code)

    validate_upload_file(filename, content_type, file_size)



    with transaction.atomic():

        validate_code_quota(user, validated.sample_code, file_size)



        s3_key = build_recording_s3_key(

            validated.year_sampled,

            validated.sample_code.code,

            filename,

        )



        return BirdRecordingUpload.objects.create(

            grower=user,

            sample_code=validated.sample_code,

            year_sampled=validated.year_sampled,

            s3_key=s3_key,

            original_filename=Path(filename).name,

            content_type=(content_type or 'application/octet-stream').split(';')[0].strip(),

            file_size_bytes=file_size,

            status=BirdRecordingUpload.STATUS_PENDING,

        )





def complete_upload(user, upload_id: int) -> BirdRecordingUpload:

    try:

        record = BirdRecordingUpload.objects.select_related('sample_code').get(

            pk=upload_id,

            grower=user,

        )

    except BirdRecordingUpload.DoesNotExist:

        raise BirdRecordingValidationError('Upload session not found.')



    if record.status == BirdRecordingUpload.STATUS_COMPLETED:

        return record



    if not s3_configured():

        raise BirdRecordingValidationError('Cloud storage is not configured.')



    client = get_media_s3_client()

    bucket = settings.AWS_STORAGE_BUCKET_NAME_MEDIA

    try:

        head = client.head_object(Bucket=bucket, Key=record.s3_key)

    except ClientError as exc:

        record.status = BirdRecordingUpload.STATUS_FAILED

        record.save(update_fields=['status'])

        raise BirdRecordingValidationError(

            'Upload was not found in storage. Please try uploading again.'

        ) from exc



    actual_size = head.get('ContentLength', 0)

    if actual_size != record.file_size_bytes:

        record.status = BirdRecordingUpload.STATUS_FAILED

        record.save(update_fields=['status'])

        raise BirdRecordingValidationError(

            f'Uploaded file size ({actual_size} bytes) does not match expected size '

            f'({record.file_size_bytes} bytes).'

        )



    with transaction.atomic():

        # Re-check quota excluding this pending row (about to complete).

        other_used = (

            BirdRecordingUpload.objects.filter(

                grower=user,

                sample_code=record.sample_code,

                status__in=(

                    BirdRecordingUpload.STATUS_COMPLETED,

                    BirdRecordingUpload.STATUS_PENDING,

                ),

            )

            .exclude(pk=record.pk)

            .aggregate(total=Sum('file_size_bytes'))['total']

        )

        other_used = int(other_used or 0)

        if other_used + record.file_size_bytes > BIRD_RECORDING_MAX_BYTES_PER_CODE:

            record.status = BirdRecordingUpload.STATUS_FAILED

            record.save(update_fields=['status'])

            raise BirdRecordingValidationError(

                'Total uploads for this sample code would exceed the 1 GB limit.'

            )



        record.status = BirdRecordingUpload.STATUS_COMPLETED

        record.uploaded_at = django_timezone.now()

        record.save(update_fields=['status', 'uploaded_at'])



    return record


