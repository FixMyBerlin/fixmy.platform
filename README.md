# fixmy.platform

[![Build Status](https://semaphoreci.com/api/v1/hekele/fixmy-platform/branches/master/badge.svg)](https://semaphoreci.com/hekele/fixmy-platform)

## Development environment

To setup the backend development environment you need to install the docker
tool on your local machine and setup accounts with Amazon AWS and Heroku. Then
you can setup docker from the checked out Git repository and import the
datasets from either Amazon or Heroku.

First things first: create a file `.env` in the project root and enter
environment variables that you want to have available during runtime. The `sample.env`
file contains some keys that you might want to have there. Most importantly this
should contain access keys used to load data from S3 and toggles used to enable
or disable certain features in the app.

A local development environment can then be set up with Docker Compose:

    $ docker-compose up -d --build

Now, the API methods are available at [http://localhost:8000/api](http://localhost:8000/api).
You can use this command whenever you want to start the development server.
When you change environment variables you need to stop the docker app with

    $ docker-compose down

and restart it with the `up` command.

Use the command

    $ docker-compose exec app bash

to access the console of the docker container running the backend app. Here you 
can use the following Python commands to manage the Django app.

# Django Manager

Use

    $ python manage.py

to get an overview of all commands available. With

    $ python manage.py createsuperuser

you create a new user for Django's admin console, which can then be accessed
at [http://localhost:8000/admin/](http://localhost:8000/admin/). You can run
the test suite with 

    $ python manage.py test

# Importing data

You can import data either by loading it from the source data files, which need
to be downloaded from Amazon S3, or by loading a data dump that you export from
the Heroku server.

## Importing data from S3

This method of importing will not import plannings and photos, which are
configured using the Django web interface. See the section for importing
from a direct dump below for that.

Get some access keys for Amazon Web Services / S3 and save them in your `.env` file
as described above. Now you can use the command

    $ python manage.py downloaddata Data/

to load all data files from S3. These are stored in the `/tmp` folder of
the docker app container.

### Legacy Data Model

You can now use `python manage.py` with the subcommands

- importedges <filename.shp>
- importplanningsections <filename.shp>
- importplanningsectiondetails <filename.csv>

to import the corresponding data. Use the subcommands in this order.

### New Data Model

You can now use `python manage.py importsections <filename>` to import the
corresponding data.

## Import Server Data Dump

This method of importing lets you access the full dataset as used in production.
For this, you run commands on the production server that export data from the
live database and then load them directly into your local machine.

Run the following commands from your regular shell to first dump all of the
model data into individual files.

```
heroku run -a fixmyplatform python manage.py dumpdata fixmyapp.Edge > Edge.json
heroku run -a fixmyplatform python manage.py dumpdata fixmyapp.Question > Question.json
heroku run -a fixmyplatform python manage.py dumpdata fixmyapp.PlanningSection > PlanningSection.json
heroku run -a fixmyplatform python manage.py dumpdata fixmyapp.PlanningSectionDetails > PlanningSectionDetails.json
heroku run -a fixmyplatform python manage.py dumpdata fixmyapp.Planning > Planning.json
heroku run -a fixmyplatform python manage.py dumpdata fixmyapp.Photo > Photo.json
```

The following commands have to be run in sequence. If they are run in
another order than specified here, the relations between entries cannot be
established correctly. Enter the container shell using 
`$ docker-compose exec app bash` and run:

```
python manage.py loaddata Edge.json
python manage.py loaddata Question.json
python manage.py loaddata PlanningSection.json
python manage.py loaddata PlanningSectionDetails.json
python manage.py loaddata Planning.json
python manage.py loaddata Photo.json
```

If all of these complete without errors you can access the app at
[localhost:8081](http://localhost:8081).
