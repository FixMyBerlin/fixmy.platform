# fixmy.platform

[![Build Status](https://semaphoreci.com/api/v1/hekele/fixmy-platform/branches/master/badge.svg)](https://semaphoreci.com/hekele/fixmy-platform)

## Development environment

First things first: create a file `.env` in the project root and enter 
environment variables that you want to have available during runtime. The `sample.env`
file contains some keys that you might want to have there. Most importantly this
should contain access keys used to load data from S3 and toggles used to enable
or disable certain features in the app.

A local development environment can then be set up with Docker Compose:

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

you create a new user for Django's admin console, which can then be accessed
at [http://localhost:8000/admin/](http://localhost:8000/admin/).

# Importing data from S3

This method of importing will not import plannings and photos, which are 
configured using the Django web interface. See the section for importing
from a direct dump below for that.

Get some access keys for Amazon Web Services / S3 and save them in your `.env` file
as described above. Now you can use the command

    $ python manage.py downloaddata Data/

to load all data files from S3. These are stored in the `/tmp` folder of 
the docker app container. 

##  Legacy Data Model

You can now use `python manage.py` with the subcommands

- importedges <filename.shp>
- importplanningsections <filename.shp>
- importplanningsectiondetails <filename.csv>

to import the corresponding data. Use the subcommands in this order.

## New Data Model

You can now use `python manage.py importsections <filename>` to import the 
corresponding data. 

# Import Server Data Dump

This method of importing lets you access the full dataset as used in production.
For this, you run a command on the production server that exports data from the
live database and sends them directly to your local machine.

The following models have to be imported in sequence. If they are imported in 
another order than specified here, the relations between entries cannot be 
established correctly.

1. Edge
2. Question
3. PlanningSection
4. PlanningSectionDetails
5. Planning
6. Photo

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

Now enter the container shell using `docker-compose exec app bash` and run the 
following commands.

```
python manage.py loaddata Edge.json
python manage.py loaddata Question.json
python manage.py loaddata PlanningSection.json
python manage.py loaddata PlanningSectionDetails.json
python manage.py loaddata Planning.json
python manage.py loaddata Photo.json
```