# fixmy.platform

[![Build Status](https://semaphoreci.com/api/v1/hekele/fixmy-platform/branches/master/badge.svg)](https://semaphoreci.com/hekele/fixmy-platform)

## Development environment

In order to use the provided development environment install [Docker Desktop](https://www.docker.com/products/docker-desktop) for Mac or Windows. On Linux, make sure you have the latest version of [Compose](https://docs.docker.com/compose/install/).

This project has a docker-compose.yml file, which will start the Django application on your local machine.

Clone the repository and start the development environment in the created directory:

    $ docker-compose up -d

Now, the API is available at [http://localhost:8000/api](http://localhost:8000/api).

Use the command

    $ docker-compose exec app bash

to access the console of the Docker container running the backend app. Here you can use the following Django commands to manage the app.

## Django commands

Use

    $ python manage.py

to get an overview of all commands available. With

    $ python manage.py createsuperuser

you create a new user for Django's admin console, which can then be accessed at [http://localhost:8000/admin/](http://localhost:8000/admin/). You can run
the test suite with

    $ python manage.py test

## Custom commands

### anonymizedata

Removes personal information from the database. By default it preserves data of staff.

    $ python manage.py anonymizedata

### downloadfiles

Downloads content of S3 bucket to /tmp, filtered by path prefix. This command requires the environment variables `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_S3_REGION_NAME` and `AWS_STORAGE_BUCKET_NAME` to be set correctly.

    $ python manage.py downloaddata Data/

### exportprojects

Exports projects as GeoJSON intended for Mapbox.

    $ python manage.py exportprojects > /tmp/projects.json

### exportsections

Exports sections as GeoJSON intended for Mapbox.

    $ python manage.py exportsections > /tmp/sections.json

### importreports

Imports reports about bike stands.

    $ python manage.py importreports /tmp/reports.json

This command requires a shape file in a format that allows GeoDjango to detect
the geometry type. GeoJSON is such a format, KML is not. All geometries must be Points.

For json file endings, field names available are guessed from the first feature
in the source file. Only these properties are then imported. If the property `id`
is available, existing reports with matching IDs are updated, if that property
is not available, new reports are created.

Caveats:

- The `fee_acceptable` field can currently not be imported.
- User likes can not be imported

Imported properties:

- address (text)
- created_date (ISO 8601 with time zone)
- description (text, limited to 1000 characters)
- id (integer)
- number (integer)
- subject (text, currently only BIKE_STANDS)
- status_reason (text)
- status (text)
  - new
  - verification
  - accepted
  - rejected
  - done

### exportreports

Export reports about bike stands in either CSV or GeoJSON format

    $ python manage.py exportreports --format geojson /tmp/reports.json

Notes:

- Likes are exported as an aggregate count
- Report creation date is exported as an ISO 8601 formatted datetime string
- CSV export uses some localized (German) table headers

### importsectiondetails

Imports section details including pictures and traffic information from CSV file. The file is usually downloaded from S3 with `downloadfiles`.

    $ python manage.py importsectiondetails /tmp/section_details.csv

### importsections

Imports sections from shape file. The file is usually downloaded from S3 with `downloadfiles`.

    $ python manage.py importsections /tmp/sections.shp

### updateprojectgeometries

Updates project geometries from a shape file. The file is usually downloaded from S3 with `downloadfiles`.

    $ python manage.py updateprojectgeometries /tmp/projects.shp linestring

### uploadtileset

Uploads GeoJSON export of projects or sections (see `exportprojects` and `exportsetcions`) to Mapbox. This command requires the environment variables `MAPBOX_UPLOAD_NAME_SECTIONS`, `MAPBOX_UPLOAD_TILESET_SECTIONS`, `MAPBOX_UPLOAD_NAME_PROJECTS` and `MAPBOX_UPLOAD_TILESET_PROJECTS` to be set correctly.

    $ python manage.py uploadtileset --dataset projects /tmp/projects.json

## Other scripts

### fetch_database

Creates a backup using a given Heroku app, downloads it and uses it to overwrite the local database schema and contents. User data is anonymized in the process, except for staff users, who are preserved.

    $ ./scripts/fetch_database.sh fixmyplatform
