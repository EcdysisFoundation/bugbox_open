import argparse
import json
import subprocess
import boto3  # requires local install


def run(cmd):
    output = subprocess.check_output(cmd.split())
    return output.decode()


def download_backup(filename):
    print('Getting heroku config....')
    app_config = json.loads(run('heroku config --json --app bugbox'))
    print('Configuring boto3 client')
    s3_client = boto3.client(
        's3',
        aws_access_key_id=app_config.get('DJANGO_AWS_ACCESS_KEY_ID', 'invalid'),
        aws_secret_access_key=app_config.get('DJANGO_AWS_SECRET_ACCESS_KEY', 'invalid'),
        region_name=app_config.get('DJANGO_AWS_REGION_NAME', 'none')
    )
    print('Downloading backup {0}'.format(filename))
    s3_client.download_file(
        app_config.get('DJANGO_AWS_STORAGE_BUCKET_NAME'),
        filename,
        'local_files/' + str(filename)
    )
    print('Completed download of {0}'.format(filename))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script to download db backup')
    parser.add_argument('filename', help='Filename of backup')
    args = parser.parse_args()
    download_backup(args.filename)
