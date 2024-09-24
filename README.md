# bugbox3

Ecdysis bugbox

[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)
[![Black code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

## Settings

Moved to [settings](http://cookiecutter-django.readthedocs.io/en/latest/settings.html).

## Basic Commands

### Setting Up Your Users

- To create a **normal user account**, just go to Sign Up and fill out the form. Once you submit it, you'll see a "Verify Your E-mail Address" page. Go to your console to see a simulated email verification message. Copy the link into your browser. Now the user's email should be verified and ready to go.

### Management, manage.py

To run commands to manage.py, use this syntax, to the appropriate .yml file

    docker compose -f local.yml run --rm django python manage.py mycommand

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

Upload backups to S3

    docker compose -f local.yml run --rm awscli upload

Download a specific backup

    docker compose -f local.yml run --rm awscli download name_of_backup.sql.gz

Restore to your database. First bring the containers down...

    docker compose -f local.yml down

bring up the db only

    docker compose -f local.yml up postgres -d

restore it to the backup file

    docker compose -f docker-compose.local.yml exec postgres restore name_of_backup.sql.gz

After it succesfully restores, bring it down and bring everything back up.

    docker compose -f local.yml down

bring all services up

    docker compose -f local.yml up

### Live reloading and Sass CSS compilation

Moved to [Live reloading and SASS compilation](https://cookiecutter-django.readthedocs.io/en/latest/developing-locally.html#sass-compilation-live-reloading).

## Deployment

The following details how to deploy this application.

### Docker

See detailed [cookiecutter-django Docker documentation](http://cookiecutter-django.readthedocs.io/en/latest/deployment-with-docker.html).

Customized for Bugbox.

local.yml is curently the only valid .yml

Custom images built are pushed to docker hub repo. Standard images used from their source. Always on the Ecdysis01 server, do not build custom docker images there. Django build may fail there at this time. Filesystem space recovery and performance of other running continers are other reasons to not build them there. Various ports are changed from default due to conflicting ports on Ecdysis01.

Bring up containers with images prebuilt

    docker compose -f local.yml up --no-build -d

Open the logs, ctrl-c to escape

    docker compose -f local.yml logs --tail=1000 --follow

If specific image needs built, specificy it individually (referring to non-custom images when on Ecdysis01)

    docker compose -f local.yml build ymlfileservicename

Locally built custom images. Push these to docker hub.

    docker push mikaylaelectra/ecdysis_django:latest

    docker push mikaylaelectra/ecdysis_celeryworker:latest

    docker push mikaylaelectra/ecdysis_celerybeat:latest

    docker push mikaylaelectra/ecdysis_flower:latest

    docker push mikaylaelectra/ecdysis_node:latest

On remote pull these down

    docker pull mikaylaelectra/ecdysis_django:latest

    docker pull mikaylaelectra/ecdysis_celeryworker:latest

    docker pull mikaylaelectra/ecdysis_celerybeat:latest

    docker pull mikaylaelectra/ecdysis_flower:latest

    docker pull mikaylaelectra/ecdysis_node:latest


### Custom Bootstrap Compilation

The generated CSS is set up with automatic Bootstrap recompilation with variables of your choice.
Bootstrap v5 is installed using npm and customised by tweaking your variables in `static/sass/custom_bootstrap_vars`.

You can find a list of available variables [in the bootstrap source](https://github.com/twbs/bootstrap/blob/v5.1.3/scss/_variables.scss), or get explanations on them in the [Bootstrap docs](https://getbootstrap.com/docs/5.1/customize/sass/).

Bootstrap's javascript as well as its dependencies are concatenated into a single file: `static/js/vendors.js`.
