#!/bin/sh -e
trap "rm -f latest.dump" EXIT INT TERM
rm -f latest.dump
# heroku pg:backups:capture -a $1
heroku pg:backups:download -a $1
docker-compose run --rm app bash -c "pg_restore -c -O -d docker latest.dump; python manage.py anonymizedata --preserve-staff; python manage.py migrate"
