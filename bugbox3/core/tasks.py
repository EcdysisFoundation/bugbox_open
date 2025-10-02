from celery import shared_task
from django.conf import settings

from bugbox3.libs.utilities import S3_CLIENT


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
