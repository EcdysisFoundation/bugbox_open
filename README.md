# bugbox3

Ecdysis bugbox

[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)

Development url, .js served in dev mode is http://localhost:3000/

## Basic Commands

### Management, manage.py

To run commands to manage.py, use this syntax, to the appropriate .yml file

    docker compose -f local.yml run --rm django python manage.py MY_COMMAND

Or to run on Heroku, using the Heroku cli to run on Production

    heroku run python manage.py MY_COMMAND -a bugbox

### Flake 8

Sort and format imports

    docker compose -f local.yml exec -T django isort bugbox3

Check other Flake8 issues

    docker compose -f local.yml exec -T django flake8 bugbox3

### Database and backups

The production database is on Heroku. A copy can be obtained for development purposes. Using local.yml for development, a postgres container is created. To restore a db to it, proceed as follows.

A script, `backup_db_s3.py` is run on Heroku at defined intervals to create long term backups or can be ran as needed to create a backup file and upload to S3.
The file is named with the date, for example 2025-04-11.dump generated the morning of April 11, 2025.

Knowing the BACKUP_FILENAME on S3, use it with the following script to download to local_files.

    python db_download_s3_backup.py BACKUP_FILENAME

Next, bring any running containers down...

    docker compose -f local.yml down

bring up the db only

    docker compose -f local.yml up postgres -d

Get the local docker postgres CONTAINER_ID.

    docker compose -f local.yml ps -q postgres

using the returned CONTAINER_ID, move the backup file from local_files to the container

    docker cp ./local_files/BACKUP_FILENAME CONTAINER_ID:/backups


Use the `restore` bash script to restore the db using the backup.

    docker compose -f local.yml exec postgres restore BACKUP_FILENAME

After it succesfully restores, bring the local db down and bring everything back up.

    docker compose -f local.yml down

bring all services up

    docker compose -f local.yml up


## Deployment

This application is deployed to Heroku for most user access scenarios at bugbox.ecdysis.bio. It is also deployed on Ecdysis01 for machine learning and inference processes. On Ecdysis01, it also uses the same Heroku database server and AWS S3 storage (see local-cloud.yml). As a result, it is important to use caution in deployment to not create conflicts when there is a potential for two different versions of the app to be running simultanously against the database and storage system. When the deployment includes database migrations the following steps should be followed. Consider other scenarios for their potential to create conflicts.

1. On Ecdsyis01, bring down the app
2. On Heroku, deploy the new version, ensure migrations run succesfully
3. Ecdysis01, pull new version from github
4. Ecdysis01, bring app back up. No migrations should run because they already ran on Heroku.

#### Deployment to Ecdysis01 server

local-cloud.yml is the .yml to use. This will establish a local Django app, and Node dev container. The database and filesystem is the production system on Heroku and AWS S3. This is not for development purposes. This is to have a Django instance running on Ecdsyis01 to manage image identifications and other needs to communicate from Ecdysis01 and Heroku database and AWS S3 storage.

If specific non-custom image needs built, specificy it individually (referring to non-custom images when on Ecdysis01)

    docker compose -f local-cloud.yml build SERVICE_NAME

The Django container image is shared with Celery containers, so if any python library changes, build all of them, on local dev environment.

    docker compose -f local.yml build django celeryworker celerybeat flower

Bring up containers with images prebuilt

    docker compose -f local-cloud.yml up --no-build -d

Open the logs, ctrl-c to escape

    docker compose -f local-cloud.yml logs --tail=1000 --follow

### Special power outage start up info on Ecdysis01.

If there is a power outage, or the Ecdysis01 server otherwise is restarted, the app has to be restarted there, starting with the Torchserve first, so that bugbox app doesnt generate a bunch of errors when it first comes up and finds that it cannot connect to Torchserve. See section below on starting Torchserve, waiting till it is full accessible to the bring up bugbox. Clear the docker network first with `docker compose -f local-cloud.yml down` then bring the containers back with `--no-build -d` as explained above, afer Torchserve fully starts.


## FastAPI

API_INFERENCE_URL is defined in settings. This relates to inference run against FastAPI hosed models, see repo https://github.com/EcdysisFoundation/inference-fastapi


## Organizations, Users, Permissions

### Setting Up Your Users

- To gain access to most UI features, the user then must be both assigned permissions to access views (see `bugbox3.core.permissions`), and be provided membership to at least one organization. When users are removed from all organizations, they also need their permssions to be revoked.

## Organizations

This app uses django-organizations ( https://github.com/bennylope/django-organizations ) to provide user access to the data of organizations they belong to. Therefore, all data access queries a user may be exposed to in the app need to properly check their organization access. Organization access is set at the model `Experiment` level. Each child table has a manager that implemnents the `user_access` function to filter data to the user's organization membership. The following examples show how to apply the filter in views.

    samples = Sample.objects.user_accesss(self.request.user).all()

A get request

    try:
        sample = Sample.objects.user_access(self.request.user).get(id=self.kwargs['sample_id'])
    except Sample.DoesNotExist:
            raise Http404

When creating new Organizations, these new Organizations will need their LookupChoices populated to be able to create Experiments and use other forms. Populate a default set of LookupChoices to get them started, by running the management command `populate_org_choices`, passing the required argument of the new organization ID.

Certain features of the app assume the first created organization is the apps primary organization. Example `bugbox3.taxonomy.constants.ECDYSIS_ORGANIZATION_ID` == 1 is defined to assume the taxonomy app Morphospecies model contents is determined by the primary organization.


## Ecdysis01 management commands

When running management commands on Ecdysis01, be the command is..

    docker compose -f local-cloud.yml run --rm django python manage.py MY_COMMAND

Several management commands and tasks are specific to Ecdysis01. Some of these are scheduled through the Celery Beat schedule. Details about some specific commands are below.


## Storages, Site-content, and Static

local.yml uses local storage and a local database
local-cloud.yml uses cloud storage and the cloud database. This should typically not be used for development.

For site static media content such as a homepage image, or a downloadable document, use core.models.PublicSiteContent to upload new media content through the Django Admin. A slugfield provides a uniqe identifier. This media is uploaded to the S3 media bucket with a public acl, instead of being set to private by default as regular media files are set. Using the slug field, a queryset can be used to insert the url to the media into the view. Note on development machines, if the local database does not have the entry, the queryset will return none, while if the entry is present, it will use the S3 url for the file.


## Development setup

For local development, the app uses Docker with the local.yml file

- `docker compose -f local.yml build`

- `docker compose -f local.yml up`

When first building and brining the app up, migrations should run succesfully creating a database generally empty of records. Docker saves the database state in a volume. In local.yml, there is an env_file entry commented out `# - ./.envs/.local/.secrets` so that the app doesnt fail if you dont have this file. The app should generally work without these vairables, but the variables may be needed if developing a feature that uses them, example an S3 integration.

- To create a **normal user account** for development of pages that dont need special user permissions, just go to Sign Up and fill out the form. Once you submit it, you'll see a "Verify Your E-mail Address" page. Go to your console to see a simulated email verification message. Copy the link into your browser. Now the user's email should be verified and ready to go.

- To assign your new user account permissions, a superuser account is required to access the Django admin to assing permissions there. Therefore, its easiest to create a superuser account instead of a normal user account. `docker compose -f local.yml run --rm django python manage.py createsuperuser` and answer the questions presented in the console.

- The app expects some permission groups for certain views and that at least one Organization exists. To create, these Django groups and assign the proper permisions to them, use the following management command, after creating your dev user.  This command will also create a default, primary organization (see organization info above). It will then add your user account to this organization and provide some default entries for the organization. Finally, your testing user can be configured in the Django adming to access the page being developed if it for example needs access to a specific Django permission group (see premission requirements for the particular view function).

`docker compose -f local.yml run --rm django python manage.py setup_app --username 'my_username'`
