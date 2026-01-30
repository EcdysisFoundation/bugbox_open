FROM docker.io/node:22-bookworm-slim AS client-builder

ARG APP_HOME=/app
WORKDIR ${APP_HOME}

COPY . ${APP_HOME}

RUN npm install && npm cache clean --force

RUN npm run buildlocal

# define an alias for the specific python version used in this file.
FROM docker.io/python:3.12.8-slim-bookworm AS python

# Python build stage
FROM python AS python-build-stage

ARG BUILD_ENVIRONMENT=localcloud
ARG APP_HOME=/app

WORKDIR ${APP_HOME}

# Install apt packages
RUN apt-get update && apt-get install --no-install-recommends -y \
  # dependencies for building Python packages
  build-essential \
  # psycopg2 dependencies
  libpq-dev

COPY --from=client-builder ${APP_HOME} ${APP_HOME}

# Create Python Dependency and Sub-Dependency Wheels.
RUN pip wheel --wheel-dir /usr/src/app/wheels  \
  -r "requirements/${BUILD_ENVIRONMENT}.txt"

# Python 'run' stage
FROM python AS python-run-stage

ARG APP_HOME=/app
WORKDIR ${APP_HOME}

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN addgroup --system django \
  && adduser --system --ingroup django django

# Install required system dependencies
RUN apt-get update && apt-get install --no-install-recommends -y \
  # Download and key management tools (needed to add external repos)
  wget \
  gnupg \
  # psycopg2 dependencies
  libpq-dev \
  # Translations dependencies
  gettext \
  # GeoDjango support libraries
  binutils \
  libproj-dev \
  gdal-bin \
  # OpenCV dependencies
  libxcb1 \
  libxcb-xinerama0 \
  libx11-xcb1 \
  libxkbcommon-x11-0 \
  libxcb-render0 \
  libxcb-shm0 \
  libsm6 \
  libxrender1 \
  libxext6 \
  libglib2.0-0 \
  # Add PostgreSQL APT repository key
  && wget -qO - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - \
  # Add PostgreSQL APT source for latest client
  && echo "deb http://apt.postgresql.org/pub/repos/apt bookworm-pgdg main" > /etc/apt/sources.list.d/pgdg.list \
  # Update again to load new PostgreSQL repo and install PostgreSQL 17 client
  && apt-get update && apt-get install --no-install-recommends -y postgresql-client-17 \
  # Cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

# All absolute dir copies ignore workdir instruction. All relative dir copies are wrt to the workdir instruction
# copy python dependency wheels from python-build-stage
COPY --from=python-build-stage /usr/src/app/wheels  /wheels/

# use wheels to install python dependencies
RUN pip install --no-cache-dir --no-index --find-links=/wheels/ /wheels/* \
  && rm -rf /wheels/

COPY --chown=django:django ./compose/production/django/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

COPY --chown=django:django ./compose/production/django/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start

COPY --chown=django:django ./compose/production/django/celery/worker/start /start-celeryworker
RUN sed -i 's/\r$//g' /start-celeryworker
RUN chmod +x /start-celeryworker

COPY --chown=django:django ./compose/production/django/celery/beat/start /start-celerybeat
RUN sed -i 's/\r$//g' /start-celerybeat
RUN chmod +x /start-celerybeat

COPY --chown=django:django ./compose/production/django/celery/flower/start /start-flower
RUN sed -i 's/\r$//g' /start-flower
RUN chmod +x /start-flower

COPY --from=python-build-stage --chown=django:django ${APP_HOME} ${APP_HOME}

RUN chown django:django ${APP_HOME}

USER django

ENTRYPOINT ["/entrypoint"]
