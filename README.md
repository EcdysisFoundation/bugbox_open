# bugbox3

Ecdysis bugbox

[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)

Development url, .js served in dev mode is http://localhost:3000/

## Basic Commands

### Setting Up Your Users

- To create a **normal user account** for development, just go to Sign Up and fill out the form. Once you submit it, you'll see a "Verify Your E-mail Address" page. Go to your console to see a simulated email verification message. Copy the link into your browser. Now the user's email should be verified and ready to go.

### Management, manage.py

To run commands to manage.py, use this syntax, to the appropriate .yml file

    docker compose -f local.yml run --rm django python manage.py mycommand

Or to run on Heroku, using the Heroku cli to run on Production

    heroku run python manage.py shell -a bugbox

### Flake 8

Sort and format imports

    docker compose -f local.yml exec -T django isort bugbox3

Check other Flake8 issues

    docker compose -f local.yml exec -T django flake8 bugbox3

### Database and backups

The production database is on Heroku. A copy can be obtained for development purposes. Using local.yml for development, a postgres container is created. To restore a db to it, proceed as follows.

A script, `backup_db_s3.py` is run on Heroku at defined intervals to create long term backups or can be ran as needed to create a backup file and upload to S3.

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


Use the `restore` bash script to restore the db using the backup. It first drops the db, then creates a blank one. As a result numerous 'errors' will report in the output where it tries to drop tables and indexes that do not exist. These can be ignored.

    docker compose -f local.yml exec postgres restore BACKUP_FILENAME

After it succesfully restores, bring the local db down and bring everything back up.

    docker compose -f local.yml down

bring all services up

    docker compose -f local.yml up


## Deployment

The following details how to deploy this application.

#### Deployment to Ecdysis01 server

local-cloud.yml is the .yml to use. This will establish a local Django app, and Node dev container. The database and filesystem is the production system on Heroku and AWS S3. This is not for development purposes. This is to have a Django instance running on Ecdsyis01 to manage image identifications and other needs to communicate from Ecdysis01 and Heroku database and AWS S3 storage.

Custom images built locally (not on Ecdysis01) and are pushed to docker hub repo. Standard images used from their source. Always on the Ecdysis01 server, do not build custom docker images there. Django build may fail there at this time. Filesystem space recovery and performance of other running continers are other reasons to not build them there. Build them locally and push to docker hub.

The Django container image is shared with Celery containers, so if any python library changes, build all of them, on local dev environment.

    docker compose -f local.yml build django celeryworker celerybeat flower

Note: Various ports are changed from default due to conflicting ports on Ecdysis01.

Locally built custom images. Push these to Docker Hub if changes are made to libraries.

    docker push mikaylaelectra/ecdysis_django:latest

    docker push mikaylaelectra/ecdysis_celeryworker:latest

    docker push mikaylaelectra/ecdysis_celerybeat:latest

    docker push mikaylaelectra/ecdysis_flower:latest

    docker push mikaylaelectra/ecdysis_node:latest

On remote pull these down, if new versions were pushed to Docker Hub

    docker pull mikaylaelectra/ecdysis_django:latest

    docker pull mikaylaelectra/ecdysis_celeryworker:latest

    docker pull mikaylaelectra/ecdysis_celerybeat:latest

    docker pull mikaylaelectra/ecdysis_flower:latest

    docker pull mikaylaelectra/ecdysis_node:latest

If specific non-custom image needs built, specificy it individually (referring to non-custom images when on Ecdysis01)

    docker compose -f local-cloud.yml build SERVICE_NAME

Bring up containers with images prebuilt

    docker compose -f local-cloud.yml up --no-build -d

Open the logs, ctrl-c to escape

    docker compose -f local-cloud.yml logs --tail=1000 --follow


### Torchserve

The image classifications performed from `taxonomy.tasks.image_prediction` are done through a Torchserve model served through Torchserve (see https://github.com/EcdysisFoundation/servemetaformer )
 produced by metaformer_ecdysis (see https://github.com/EcdysisFoundation/metaformer_ecdysis )
