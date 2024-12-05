from .base import *  # noqa
from .base import env

# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = env("DJANGO_SECRET_KEY")
# https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ["localhost", "0.0.0.0", "127.0.0.1", "bugbox-381407baad84.herokuapp.com",
                 "bugbox.ecdysis.bio"]

# DATABASES
# ------------------------------------------------------------------------------
DATABASES["default"]["CONN_MAX_AGE"] = env.int("CONN_MAX_AGE", default=60)  # noqa: F405

# Celery
CELERY_BROKER_URL = env("REDISCLOUD_URL")
# https://docs.celeryq.dev/en/stable/userguide/configuration.html#std:setting-result_backend
CELERY_RESULT_BACKEND = CELERY_BROKER_URL

# AI_INFERENCE_URL
# Set to blank on Heroku config,
#  so that its aware the URL is not accessible, due to private network.
AI_INFERENCE_URL = env("AI_INFERENCE_URL")
ON_ECDYSIS_SERVER = 'NO'

# CACHES
# ------------------------------------------------------------------------------
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": env("REDISCLOUD_URL"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            # Mimicing memcache behavior.
            # https://github.com/jazzband/django-redis#memcached-exceptions-behavior
            "IGNORE_EXCEPTIONS": True,
        },
    }
}

# SECURITY
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-proxy-ssl-header
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-ssl-redirect
SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=True)
# https://docs.djangoproject.com/en/dev/ref/settings/#session-cookie-secure
SESSION_COOKIE_SECURE = True
# https://docs.djangoproject.com/en/dev/ref/settings/#csrf-cookie-secure
CSRF_COOKIE_SECURE = True
# https://docs.djangoproject.com/en/dev/topics/security/#ssl-https
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-hsts-seconds
# TODO: set this to 60 seconds first and then to 518400 once you prove the former works
SECURE_HSTS_SECONDS = 60
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-hsts-include-subdomains
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool("DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS", default=True)
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-hsts-preload
SECURE_HSTS_PRELOAD = env.bool("DJANGO_SECURE_HSTS_PRELOAD", default=True)
# https://docs.djangoproject.com/en/dev/ref/middleware/#x-content-type-options-nosniff
SECURE_CONTENT_TYPE_NOSNIFF = env.bool("DJANGO_SECURE_CONTENT_TYPE_NOSNIFF", default=True)


# STORAGES
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

COLLECTFASTA_STRATEGY = "collectfasta.strategies.boto3.Boto3Strategy"
INSTALLED_APPS = ["collectfasta", *INSTALLED_APPS]

# EMAIL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#default-from-email
DEFAULT_FROM_EMAIL = "reports@ecdysis.bio"
# https://docs.djangoproject.com/en/dev/ref/settings/#server-email
SERVER_EMAIL = "reports@ecdysis.bio"
# https://docs.djangoproject.com/en/dev/ref/settings/#email-subject-prefix
EMAIL_SUBJECT_PREFIX = env(
    "DJANGO_EMAIL_SUBJECT_PREFIX",
    default="[bugbox3] ",
)

# Anymail
# ------------------------------------------------------------------------------
# https://anymail.readthedocs.io
INSTALLED_APPS += ["anymail"]  # noqa: F405
EMAIL_BACKEND = "anymail.backends.amazon_ses.EmailBackend"
ANYMAIL = {"AMAZON_SES_CLIENT_PARAMS": {
        "aws_access_key_id": env("DJANGO_AWS_ACCESS_KEY_ID"),
        "aws_secret_access_key": env("DJANGO_AWS_SECRET_ACCESS_KEY"),
        "region_name": env("DJANGO_AWS_REGION_NAME"),
    },}

# LOGGING
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#logging
# See https://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.

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
