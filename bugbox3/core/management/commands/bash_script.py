import subprocess

from django.conf import settings
from django.core.management.base import BaseCommand

# run like
# python manage.py bash_script /path/to/my_script.sh


class Command(BaseCommand):
    help = 'Runs a bash script'

    def add_arguments(self, parser):
        parser.add_argument('script_path', type=str, help='Path to the bash script')
        parser.add_argument(
            '--output',
            action='store_true',
            help='Show subpross stdout, use caution with large operations'
        )

    def handle(self, *args, **options):
        if settings.ON_ECDYSIS_SERVER == 'YES':
            script_path = options['script_path']
            try:
                result = subprocess.run(
                    ['bash', script_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                if result.returncode == 0:
                    if options['output']:
                        self.stdout.write(result.stdout)
                    self.stdout.write('bash_script {0} completed successfully'.format(script_path))
                else:
                    raise Exception(f"Script execution failed: {result.stderr}")
            except Exception as e:
                raise Exception(f"Error running script: {e}")
        else:
            print('Currently this cmd is only supported on Ecdysis01')
