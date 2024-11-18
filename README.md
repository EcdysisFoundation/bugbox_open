# bugbox3

Ecdysis bugbox

[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)
[![Black code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

Development url, .js served in dev mode is http://localhost:3000/

Production url with .js served from /static/ is http://localhost:8002/

## Settings

Moved to [settings](http://cookiecutter-django.readthedocs.io/en/latest/settings.html).

## Basic Commands

### Setting Up Your Users

- To create a **normal user account**, just go to Sign Up and fill out the form. Once you submit it, you'll see a "Verify Your E-mail Address" page. Go to your console to see a simulated email verification message. Copy the link into your browser. Now the user's email should be verified and ready to go.

### Management, manage.py

To run commands to manage.py, use this syntax, to the appropriate .yml file

    docker compose -f local.yml run --rm django python manage.py mycommand

or to run on Heroku, using the Heroku cli

    heroku run python manage.py shell -a bugbox

### Flake 8

Sort and format imports

    docker compose -f local.yml exec -T django isort bugbox3

Check other Flake8 issues

    docker compose -f local.yml exec -T django flake8 bugbox3

### Database backups

Database backups are configured with Cookie cutter methods. In our case it is expanded to the local version to aid in development. Seperate AWS IAM users are configured for different envirionments

use bugbox-local user access keys for local.yml use cases, whle bugbox-localserver is for localserver.yml cases. These .yml files should reference a .secrets file in the repo .env directory that defines the environment variables and is gitignored to keep it secret.

Initiate a backup in docker

    docker compose -f local.yml exec postgres backup

List backups

    docker compose -f local.yml exec postgres backups

Upload backups to S3

    docker compose -f local.yml run --rm awscli upload

Download a specific backup

    docker compose -f local.yml run --rm awscli download BACKUP_FILE

Restore to your database. First bring the containers down...

    docker compose -f local.yml down

bring up the db only

    docker compose -f local.yml up postgres -d

restore it to the backup file

    docker compose -f local.yml exec postgres restore BACKUP_FILE

After it succesfully restores, bring it down and bring everything back up.

    docker compose -f local.yml down

bring all services up

    docker compose -f local.yml up

Alternatvely to using the AWS CLI, a backup can be downloaded directly from the Ecdysis01 server. This process includes moving the file out and in the docker conatiner.

With a backup already created in the Ecdysis01 docker container as described above, get the container ID ...

    docker compose -f local.yml ps -q postgres

using the returned CONTAINER_ID, move the backup file from the container to a directory named backups in the bugbox3 directory.

    docker cp CONTAINER_ID:/backups/BACKUP_FILE ./backups/BACKUP_FILE

Then use scp to copy this file to local computer.

    scp ecdysis@ecdysis01.local:/srv/bugbox3/backups/BACKUP_FILE backups/BACKUP_FILE

Get the local docker container id.

    docker compose -f local.yml ps -q postgres

Copy the backup to it

    docker cp ./backups/BACKUP_FILE CONTAINER_ID:/backups

### Live reloading and Sass CSS compilation

Moved to [Live reloading and SASS compilation](https://cookiecutter-django.readthedocs.io/en/latest/developing-locally.html#sass-compilation-live-reloading).

## Deployment

The following details how to deploy this application.

### Docker and BugBox app

See detailed [cookiecutter-django Docker documentation](http://cookiecutter-django.readthedocs.io/en/latest/deployment-with-docker.html).

Customized for Bugbox.

local.yml is curently the only valid .yml

Custom images built are pushed to docker hub repo. Standard images used from their source. Always on the Ecdysis01 server, do not build custom docker images there. Django build may fail there at this time. Filesystem space recovery and performance of other running continers are other reasons to not build them there.

Various ports are changed from default due to conflicting ports on Ecdysis01.

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

    docker compose -f local.yml build SERVICE_NAME

Bring up containers with images prebuilt

    docker compose -f local.yml up --no-build -d

Open the logs, ctrl-c to escape

    docker compose -f local.yml logs --tail=1000 --follow

NODE: If changes are made to webpack built .js, then once deployed and fully started, need to rebuild those files to /static/.

    docker compose -f local.yml exec -it node sh -c "npm run build"

NODE: Bring the node container down. This is not needed to run the dev port 3000 on production, after "npm run build" is ran.

    docker compose -f local.yml down node

### Torchserve

The image classifications performed from `taxonomy.tasks.image_prediction` are done through a Torchserve model served through Torchserve (see https://github.com/EcdysisFoundation/servemetaformer )
 produced by metaformer_ecdysis (see https://github.com/EcdysisFoundation/metaformer_ecdysis )


### Custom Bootstrap Compilation

The generated CSS is set up with automatic Bootstrap recompilation with variables of your choice.
Bootstrap v5 is installed using npm and customised by tweaking your variables in `static/sass/custom_bootstrap_vars`.

You can find a list of available variables [in the bootstrap source](https://github.com/twbs/bootstrap/blob/v5.1.3/scss/_variables.scss), or get explanations on them in the [Bootstrap docs](https://getbootstrap.com/docs/5.1/customize/sass/).

Bootstrap's javascript as well as its dependencies are concatenated into a single file: `static/js/vendors.js`.
