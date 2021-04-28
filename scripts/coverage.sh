#!/bin/sh -e
DEBUGPY=0 coverage run --source=fixmyapp,survey,reports,permits --omit='*/tests/*' manage.py test -v 3
coverage report --skip-covered --skip-empty --show-missing
coverage xml -o coverage.xml