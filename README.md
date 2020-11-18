# fixmy.platform

![CI](https://github.com/FixMyBerlin/fixmy.platform/workflows/CI/badge.svg)

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

## Custom Commands: fixmyapp

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

### exportplaystreets

Similar to `exportreports`, this command exports play street signups to a csv file.

    $ python manage.py exportplaystreets spielstrassen.csv

### exportgastrosignups

This command exports GastroSignup entries, either in CSV or GeoJSON format. The GeoJSON format has an additional switch that allows exporting usage areas instead of the geolocation of the entry's shop.

The CSV format doesn't include usage areas and uploaded certificates.

The GeoJSON format doesn't include any personal information.

In order to export the requested usage areas in GeoJSON format into a file `gastrosignup_area.geojson`:

    $ python manage.py exportgastrosignups --format geojson --area gastrosignup_area.geojson

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

## Custom Commands: reports

### exportreports

Export reports about bike stands in either CSV or GeoJSON format

    $ python manage.py exportreports --format csv /tmp/reports.csv

Notes:

- Likes are exported as an aggregate count
- Report creation date is exported as an ISO 8601 formatted datetime string

### importreports

Import or update entries in the reports app from a CSV file.

The imported CSV file is required to have the columns;

- origin_ids: semicolon-separated list of reports that are implemented by this planning
- status: one of the report statuses as can be found in `reports.models.report`
- address: address including post code
- lat
- long
- description: a description of the planning
- status_reason: a reason if the planning's status is 'invalid'
- number: number of bike stands built in this planning

  \$ python manage.py importreports reports.csv

### sendnotifications

Batch send notifications, which are enqueued when a reports status is changed

    $ python manage.py sendnotifications

## Other scripts

### fetch_database

Creates a backup using a given Heroku app, downloads it and uses it to overwrite the local database schema and contents. User data is anonymized in the process, except for staff users, who are preserved.

    $ ./scripts/fetch_database.sh fixmyplatform
