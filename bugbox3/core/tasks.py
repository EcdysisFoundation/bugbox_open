from celery import shared_task
from django.conf import settings
from django.core.management import call_command

from ..libs.utilities import S3_CLIENT


@shared_task()
def download_s3_media(source_obj, destination_path):

    if settings.ON_ECDYSIS_SERVER != 'YES':
        print('Currently this task is only supported on Ecdysis01')
        return

    S3_CLIENT.download_file(
        Bucket=settings.AWS_STORAGE_BUCKET_NAME_MEDIA,
        Key=source_obj,
        Filename=destination_path
    )
    return

@shared_task(
    soft_time_limit=600,
    time_limit=660,
)
def backup_db_to_s3_task():
    print("Starting database backup to S3...")
    call_command('backup_db_to_s3')
    print("Finished database backup to S3.")