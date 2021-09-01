#!/bin/bash
set -e

# if first arg looks like a flag, assume we want to run gunicorn server
if [ "${1:0:1}" = '-' ]; then
  set -- gunicorn "$@"
fi

if [ "$1" = "gunicorn" ]; then
  python manage.py migrate
  python manage.py collectstatic
fi

exec "$@"
