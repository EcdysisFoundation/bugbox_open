 # myapp/management/commands/run_my_script.py
import subprocess

from django.core.management.base import BaseCommand


# run like
# python manage.py bash_script /path/to/my_script.sh


class Command(BaseCommand):
    help = 'Runs a bash script'

    def add_arguments(self, parser):
        parser.add_argument('script_path', type=str, help='Path to the bash script')

    def handle(self, *args, **options):
        script_path = options['script_path']
        try:
            result = subprocess.run(['bash', script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode == 0:
                self.stdout.write('bash_script {0} completed successfully'.format(script_path))
                # or write all output, with caution on large operations
                # self.stdout.write(result.stdout)
            else:
                raise Exception(f"Script execution failed: {result.stderr}")
        except Exception as e:
            raise Exception(f"Error running script: {e}")
