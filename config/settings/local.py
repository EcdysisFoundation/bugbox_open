from .base import *  # noqa
from .base import env
import os


# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = True
# https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    default="Vg7uq2A2ICRRuh8dEgynpQxQ4GPs2Gm23A6vTNCYoyXXOb7ps7nN5ZBU1LYVM1PX",
)
# https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = [
    "localhost", "0.0.0.0", "127.0.0.1", "ecdysis01", "ecdysis01.local", "172.30.0.7", "10.147.19.124",
    "216.106.203.179", "172.16.16.147",
    ".localhost", ".local", "172.30.0.8", "django", "192.168.16.8", "[::1]"
]

# CACHES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#caches
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "",
    }
}

# EMAIL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = env("DJANGO_EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend")

# django-debug-toolbar
# ------------------------------------------------------------------------------
# https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#prerequisites
INSTALLED_APPS += ["debug_toolbar"]  # noqa: F405
# https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#middleware
MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]  # noqa: F405
# https://django-debug-toolbar.readthedocs.io/en/latest/configuration.html#debug-toolbar-config
DEBUG_TOOLBAR_CONFIG = {
    "DISABLE_PANELS": [
        "debug_toolbar.panels.history.HistoryPanel",
        "debug_toolbar.panels.versions.VersionsPanel",
        "debug_toolbar.panels.timer.TimerPanel",
        "debug_toolbar.panels.settings.SettingsPanel",
        "debug_toolbar.panels.headers.HeadersPanel",
        "debug_toolbar.panels.request.RequestPanel",
        "debug_toolbar.panels.staticfiles.StaticFilesPanel",
        "debug_toolbar.panels.templates.TemplatesPanel",
        "debug_toolbar.panels.alerts.AlertsPanel",
        "debug_toolbar.panels.cache.CachePanel",
        "debug_toolbar.panels.signals.SignalsPanel",
        "debug_toolbar.panels.profiling.ProfilingPanel",
        "debug_toolbar.panels.redirects.RedirectsPanel"
    ],
    "SHOW_TEMPLATE_CONTEXT": True,
    "SHOW_TOOLBAR_CALLBACK": "bugbox3.core.permissions.show_toolbar"
}
# https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#internal-ips
INTERNAL_IPS = ["127.0.0.1", "10.0.2.2"]
if env("USE_DOCKER") == "yes":
    import socket

    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS += [".".join(ip.split(".")[:-1] + ["1"]) for ip in ips]
    try:
        _, _, ips = socket.gethostbyname_ex("node")
        INTERNAL_IPS.extend(ips)
    except socket.gaierror:
        # The node container isnt started (yet?)
        pass

# Celery
# ------------------------------------------------------------------------------

# https://docs.celeryq.dev/en/stable/userguide/configuration.html#task-eager-propagates
CELERY_TASK_EAGER_PROPAGATES = True
# https://docs.celeryq.dev/en/stable/userguide/configuration.html#std:setting-broker_url

CELERY_BROKER_URL = env("CELERY_BROKER_URL")
# https://docs.celeryq.dev/en/stable/userguide/configuration.html#std:setting-result_backend
CELERY_RESULT_BACKEND = CELERY_BROKER_URL

# set this to YES in env variable on ECDYSIS01
ON_ECDYSIS_SERVER = env("ON_ECDYSIS_SERVER", default='NO')

# django-webpack-loader
# ------------------------------------------------------------------------------
WEBPACK_LOADER["DEFAULT"]["CACHE"] = not DEBUG  # noqa: F405


###########################
# USE CLOUD STORAGE IF THESE SETTINGS ENABLED
if ON_ECDYSIS_SERVER.upper() == "YES":
    # Use cloud (S3) storage on Ecdysis01 or cloud instances
    aws_s3_domain_media = f"{AWS_STORAGE_BUCKET_NAME_MEDIA}.s3.amazonaws.com"
    aws_s3_domain_static = f"{AWS_STORAGE_BUCKET_NAME_STATIC}.s3.amazonaws.com"
    # STATIC & MEDIA
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3.S3Storage",
            "OPTIONS": {
                "file_overwrite": False,
                "bucket_name": AWS_STORAGE_BUCKET_NAME_MEDIA
            },
        },
        "staticfiles": {
            "BACKEND": "storages.backends.s3.S3Storage",
            "OPTIONS": {
                "default_acl": "public-read",
                "bucket_name": AWS_STORAGE_BUCKET_NAME_STATIC
            },
        },
    }

    MEDIA_URL = f"https://{aws_s3_domain_media}/"
    STATIC_URL = f"https://{aws_s3_domain_static}/"

    # Collectfasta
    # ------------------------------------------------------------------------------
    # https://github.com/jasongi/collectfasta#installation
    # Enable collectfasta only in cloud mode
    COLLECTFASTA_STRATEGY = "collectfasta.strategies.boto3.Boto3Strategy"
    INSTALLED_APPS = ["collectfasta", *INSTALLED_APPS]

else:
    # Use local file storage in dev mode
    MEDIA_URL = "/media/"
    STATIC_URL = "/static/"
