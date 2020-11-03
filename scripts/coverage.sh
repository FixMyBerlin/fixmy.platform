#!/bin/sh -e
coverage run --source=fixmyapp,survey,reports --omit='*/tests/*' manage.py test
coverage report --skip-covered --skip-empty --show-missing
coverage xml -o coverage.xml