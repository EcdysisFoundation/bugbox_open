import os
import subprocess
import boto3
import datetime


def save_backup_s3():
    """
    Backup Heroku database and save to AWS S3
    """
    aws_access_key_id = os.environ.get('DJANGO_AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.environ.get('DJANGO_AWS_SECRET_ACCESS_KEY')
    aws_bucket_name = os.environ.get('DJANGO_AWS_STORAGE_BUCKET_NAME')
    db_url = os.environ.get('DATABASE_URL')

    has_all_settings = all([aws_access_key_id, aws_secret_access_key, aws_bucket_name, db_url])
    assert has_all_settings, 'Missing required settings to run backup!'

    backup_filename = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d.dump')
    cmd = 'pg_dump -Fc --no-acl --no-owner {url} > {file}'.format(url=db_url, file=backup_filename)
    subprocess.run(cmd, shell=True)

    s3_client = boto3.client(
        's3',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )
    s3_client.upload_file(backup_filename, aws_bucket_name, backup_filename)


if __name__ == '__main__':
    save_backup_s3()
