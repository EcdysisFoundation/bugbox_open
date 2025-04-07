import os

from celery import Celery
from celery.schedules import crontab
from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

app = Celery("bugbox3")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

if settings.ON_ECDYSIS_SERVER == "YES":
    app.conf.beat_schedule = {
        'run_classify_new_images': {
            'task': 'bugbox3.taxonomy.tasks.run_classify_new_images',
            'schedule': crontab(minute=0)
        },
        'run_update_classifications': {
            'task': 'bugbox3.taxonomy.tasks.run_update_classifications',
            'schedule': crontab(minute=30)
        },
        'run_s3_media_download': {
            'task': 'bugbox3.taxonomy.tasks.run_s3_media_download',
            'schedule': crontab(day_of_week=5, hour=22, minute=5)
        },
        'run_set_public_images':  {
            'task': 'bugbox3.taxonomy.tasks.run_set_public_images',
            'schedule': crontab(hour=20)
        },
        'run_refresh_public_exports': {
            'task': 'bugbox3.taxonomy.tasks.run_refresh_public_exports',
            'schedule': crontab(day_of_month=1, hour=21, minute=5)
        }
    }
