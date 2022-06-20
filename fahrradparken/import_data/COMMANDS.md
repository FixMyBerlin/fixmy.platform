# Command line documentation to check, delete and import data

```
docker compose up -d
```

## Copy Data-Folder into the Docker instance

```
./manage.py downloadfiles Data/
```

## Reset data / delete everything

```
docker compose exec app bash

./manage.py shell
from fahrradparken.models import Station, ParkingFacility
// check non-0
Station.objects.count()
ParkingFacility.objects.count()
// delete
Station.objects.all().delete()
// check 0
Station.objects.count()
ParkingFacility.objects.count()
// ctrl+d to close shell
```

## Import stations

```
docker compose exec app bash

./manage.py importstations ./fahrradparken/import_data/2021-12-06/stations-v1.0-original.geojson  2>&1 | tee ./fahrradparken/import_data/2021-12-06/stations-v1.0-original.log

./manage.py importstations ./fahrradparken/import_data/2021-12-13/stations-fehlende.geojson  2>&1 | tee ./fahrradparken/import_data/2021-12-13/stations-fehlende.log

// Check
./manage.py shell
from fahrradparken.models import Station, ParkingFacility
Station.objects.count()
```

Delete only OSM:

```
from fahrradparken.models import ParkingFacility
ParkingFacility.objects.filter(source__startswith='©').count()
ParkingFacility.objects.filter(source__startswith='©').delete()
```

## Import parkingfacilities

```
docker compose exec app bash

// Check
./manage.py shell
from fahrradparken.models import ParkingFacility
ParkingFacility.objects.count()
// ctrl+d

./manage.py importparkingfacilities ./fahrradparken/import_data/2021-12-13/fahrradabstellanlagen-bahnstadt-bereinigt.csv --delimiter=","  2>&1 | tee ./fahrradparken/import_data/2021-12-13/fahrradabstellanlagen-bahnstadt-bereinigt.log

./manage.py importparkingfacilities ./fahrradparken/import_data/2021-12-13/fahrradabstellanlagen-osm-v4.csv --skip-stations=./fahrradparken/import_data/2021-12-13/skiplist.csv --delimiter=";"  2>&1 | tee ./fahrradparken/import_data/2021-12-13/fahrradabstellanlagen-osm-v4.log
```
