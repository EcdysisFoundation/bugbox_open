from .base import *  # noqa
from .base import env


# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = False
# https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    default="Vg7uq2A2ICRRuh8dEgynpQxQ4GPs2Gm23A6vTNCYoyXXOb7ps7nN5ZBU1LYVM1PX",
)
# https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = env.list(
    "DJANGO_ALLOWED_HOSTS",
    default=[
        "localhost",
        "0.0.0.0",
        "127.0.0.1",
        ".localhost",
        ".local",
        "django",
        "[::1]",
    ],
)
CSRF_TRUSTED_ORIGINS = env.list(
    "DJANGO_CSRF_TRUSTED_ORIGINS",
    default=["http://localhost:3000"],
)

STITCHER_API_URL = env(
    "STITCHER_API_URL",
    default="http://host.docker.internal:8090",
)
STITCHER_JS_URL = env("STITCHER_JS_URL", default="")
STITCHER_JS_URL_ZEROTIER = env("STITCHER_JS_URL_ZEROTIER", default="")
STITCHER_FLOWER_URL = env("STITCHER_FLOWER_URL", default="")

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
# mounted as volume in local-cloud.yml
LOCAL_MOUNTED_MEDIA = env("LOCAL_MOUNTED_MEDIA", default="/mounted_local_media/")
S3_DOWNLOAD_MEDIA_SOURCE_PREFIX = env("S3_DOWNLOAD_MEDIA_SOURCE_PREFIX", default="")

# Use cloud (S3) storage on Ecdysis01 for media, but not static
aws_s3_domain_media = f"{AWS_STORAGE_BUCKET_NAME_MEDIA}.s3.amazonaws.com"
STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "file_overwrite": False,
            "bucket_name": AWS_STORAGE_BUCKET_NAME_MEDIA
        },
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    }
}

MEDIA_URL = f"https://{aws_s3_domain_media}/"
# serve static locally
STATIC_URL = "/static/"


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {"require_debug_false": {"()": "django.utils.log.RequireDebugFalse"}},
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s",
        },
    },
    "handlers": {
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {"level": "INFO", "handlers": ["console"]},
    "loggers": {
        "django.request": {
            "handlers": ["mail_admins"],
            "level": "ERROR",
            "propagate": True,
        },
        "django.security.DisallowedHost": {
            "level": "ERROR",
            "handlers": ["console", "mail_admins"],
            "propagate": True,
        },
    },
}
