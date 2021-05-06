#!/bin/sh -e
trap "rm -f latest.dump" EXIT INT TERM
rm -f latest.dump
# heroku pg:backups:capture -a $1
heroku pg:backups:download -a $1
docker-compose run --rm app bash -c "dropdb docker && createdb docker && pg_restore --clean --no-owner --dbname docker latest.dump; python manage.py anonymizedata --preserve-staff; python manage.py migrate"
