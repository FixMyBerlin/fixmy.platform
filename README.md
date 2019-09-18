# fixmy.platform

[![Build Status](https://semaphoreci.com/api/v1/hekele/fixmy-platform/branches/master/badge.svg)](https://semaphoreci.com/hekele/fixmy-platform)

## Development environment

- how to create an .env file

A local development environment can now be set up with Docker Compose.

    $ docker-compose up -d --build

Now, the API methods are available at [http://localhost:8000/api](http://localhost:8000/api).

Use the command `docker-compose exec app bash` to access the console of the 
docker container running the backend app. Here you can use the following 
Python commands to manage the Django app.

# Django Manager

Use 
    $ python manage.py test

to get an overview of all commands available. With 

    $ python manage.py createsuperuser

you can create a new user for Django's admin console, which can then be accessed
at [http://localhost:8000/admin/](http://localhost:8000/admin/).

# Importing data from S3 (legacy model)

- create an S3 user and get access keys
- save them to .env
- python manage.py downloaddata

saves data to /tmp/

- python manage.py importedges -v3 /tmp/Detail...shp
- python manage.py importplanningsections -v3 /tmp/Abschnitte...

# Importing data from S3 (new model)

...

# import von heroku

- heroku run -a fixmyplatform python manage.py dumpdata fixmyapp.<Model> > <model>.json

1. edges
2. questions
3. planning_sections
4. planning_section_details
5. plannings
6. photos