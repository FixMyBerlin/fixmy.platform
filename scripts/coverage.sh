#!/bin/sh -e
coverage run --source='.' manage.py test
coverage report --skip-covered --skip-empty -m
coverage xml -o cov.xml