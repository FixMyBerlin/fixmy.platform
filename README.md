# fixmy.platform

![CI](https://github.com/FixMyBerlin/fixmy.platform/workflows/CI/badge.svg)

## Development environment

In order to use the provided development environment install [Docker Desktop](https://www.docker.com/products/docker-desktop) for Mac or Windows. On Linux, make sure you have the latest version of [Compose](https://docs.docker.com/compose/install/).

This project has a docker-compose.yml file, which will start the Django application on your local machine.

### 1. Setup Docker

Clone the repository and start the development environment in the created directory:

```
docker-compose up -d
```

(Should you recieve errors [like `docker/transport/unixconn.py`](https://github.com/prisma/prisma1/issues/5120#issue-700225976), try starting docker desktop first, then run the compose command.)

### 2. Test API

Now, the API is available at [http://localhost:8000/api/](http://localhost:8000/api/).

```
curl http://localhost:8000/api/
# => {"users":"http://localhost:8000/api/users/"}
```

### 3. Configure Django

Access the console of the Docker container running the backend app:

```
docker-compose exec app bash
```

#### 3.1 Create a new user for Django's admin console

[http://localhost:8000/admin/](http://localhost:8000/admin/)

```
python manage.py createsuperuser
```

#### 3.2 Seed data

_TODO_

### Code Editor VSCode

#### "black" code formatter

Please use black as code formatter. https://black.readthedocs.io/en/stable/

We use `# fmt: off` whenever we want to specify our own formatting style.

VSCode hints:

- Use "Format Document" to manually format
- Install the [Microsoft Python Extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python) for VSCode
  - Configure "Python > Formatting Provider": "Black" (`"python.formatting.provider": "black"`)
- Make sure your VSCode Python Version in "Python: Select interpreter" sie same as your docker terminal `root@123406906c90:/code# which python`

### Docker support

Using the [Docker extension](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-docker)
is recommended to develop in VSCode. It requires special `./.devcontainer` setting files hat a fellow developer can provide.

## Configuration

Configuration options are set through environment variables, all of which are listed in [`docker-compose.yml`](./docker-compose.yml).

### AWS Backend

.

### General Debugging

.

### E-Mail Service

.

### Mapbox service

.

### Newsletter service

.

### [Reports app](./reports)

.

### [Gastro app](.#todo)

_TODO: Does this have a folder?_

### [Permits app](./permits)

`EVENT_RECIPIENT` (string): An email address to which email notifications for
accepted or rejected applications are sent be forwarded to the actual recipients.

`EVENT_SIGNUPS_OPEN` (string): An iso 8601 formatted datetime which defines the
beginning of the event permit application signup timeframe.

If undefined, applications are always open. If the value can not be parsed, sign
ups are always closed.

`EVENT_SIGNUPS_CLOSE` (string): Equivalent for closing date and time.

### [Playstreets app](#todo)

_TODO: Does this have a folder?_

## Django commands

- Get an overview of all commands available:

  ```
  docker-compose exec app bash
  python manage.py
  ```

- Run the test suite:

  ```
  docker-compose exec app bash
  python manage.py test
  ```

- Run the test suite with pdb for debugging

  ```
  ./manage.py test --pdb
  ```

## Debugging

**Using debugpy:**

You can enable interactive debugging through [debugpy](https://github.com/microsoft/debugpy) by setting the environment variable `DEBUGPY=1` (e.g. through a `.env` file).

**Using pdb:**

- Docs https://docs.python.org/3/library/pdb.html
- `import pdb; pdb.set_trace()` – Break into the debugger from a running program.
- `l` – List source code for the current file.
- `a` – Print the argument list of the current function.
- `p some_variable` – Evaluate the expression in the current context and print its value.

## Custom Commands: fixmyapp

### anonymizedata

Removes personal information from the database. By default it preserves data of staff.

```
python manage.py anonymizedata
```

### downloadfiles

Downloads content of S3 bucket to /tmp, filtered by path prefix. This command requires the environment variables `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_S3_REGION_NAME` and `AWS_STORAGE_BUCKET_NAME` to be set correctly.

```
python manage.py downloaddata Data/
```

### exportprojects

Exports projects as GeoJSON intended for Mapbox.

```
python manage.py exportprojects > /tmp/projects.json
```

### exportsections

Exports sections as GeoJSON intended for Mapbox.

```
python manage.py exportsections > /tmp/sections.json
```

### exportplaystreets

Similar to `exportreports`, this command exports play street signups to a csv file.

```
python manage.py exportplaystreets spielstrassen.csv
```

### exportgastrosignups

This command exports GastroSignup entries, either in CSV or GeoJSON format. The GeoJSON format has an additional switch that allows exporting usage areas instead of the geolocation of the entry's shop.

The CSV format doesn't include usage areas and uploaded certificates.

The GeoJSON format doesn't include any personal information.

In order to export the requested usage areas in GeoJSON format into a file `gastrosignup_area.geojson`:

```
python manage.py exportgastrosignups --format geojson --area gastrosignup_area.geojson
```

### updatehbi

Bootstrap the database for HBI. Downloads and imports road and intersection data, section details and section accidents, also applying migrations.

```
python manage.py updatehbi
```

### importsections

Imports sections from shape file. The file is usually downloaded from S3 with `downloadfiles`.

```
python manage.py importsections /tmp/sections.shp
```

### importsectiondetails

Imports section details including pictures and traffic information from CSV file. The file is usually downloaded from S3 with `downloadfiles`.

```
python manage.py importsectiondetails /tmp/section_details.csv
```

### importsectionaccidents

Import section accident data set, which references previously imported sections.

```
python manage.py importsectionaccidents /tmp/section_accidents.csv
```

### updateprojectgeometries

Updates project geometries from a shape file. The file is usually downloaded from S3 with `downloadfiles`.

```
python manage.py updateprojectgeometries /tmp/projects.shp linestring
```

### uploadtileset

Uploads GeoJSON export of projects or sections (see `exportprojects` and `exportsetcions`) to Mapbox. This command requires the environment variables `MAPBOX_UPLOAD_NAME_SECTIONS`, `MAPBOX_UPLOAD_TILESET_SECTIONS`, `MAPBOX_UPLOAD_NAME_PROJECTS` and `MAPBOX_UPLOAD_TILESET_PROJECTS` to be set correctly.

```
python manage.py uploadtileset --dataset projects /tmp/projects.json
```

## Custom Commands: reports

### exportreports

Export reports about bike stands in either CSV or GeoJSON format

```
python manage.py exportreports --format csv /tmp/reports.csv
```

Notes:

- Likes are exported as an aggregate count
- Report creation date is exported as an ISO 8601 formatted datetime string

### importreports

Import or update entries in the reports app from a CSV file.

The imported CSV file is required to have the columns;

- id: entry id that should be updated by this row. Leave empty to create new entries.
- origin_ids: semicolon-separated list of reports that are implemented by this planning
- status: one of the report statuses as can be found in `reports.models.report`
- address: address including post code
- lat
- long
- description: a description of the planning
- status_reason: a reason if the planning's status is 'invalid'
- number: number of bike stands built in this planning

```
python manage.py importreports reports.csv
```

### sendnotifications

Batch send notifications, which are enqueued when a reports status is changed

```
python manage.py sendnotifications
```

This command requires the environment variables `REPORTS_NOTIFICATION_CAMPAIGN`
and `REPORTS_NOTIFICATION_SENDER` to be set. You can send sample emails
containing all variations of the text templates using

```
python manage.py sendnotifications --send-samples your@email.org
```

## Other scripts

### fetch_database

Creates a backup using a given Heroku app, downloads it and uses it to overwrite the local database schema and contents. User data is anonymized in the process, except for staff users, who are preserved.

_todo: Requires heroku tools? Only for heroku based installations._

```
./scripts/fetch_database.sh fixmyplatform
```
