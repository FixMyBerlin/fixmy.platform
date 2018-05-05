# Deployment

## Prerequisites

1. Install gcloud from https://cloud.google.com/sdk/docs/.
1. Install gcloud components: `$ gcloud components install kubectl docker-credential-gcr`.
1. Create docker credential configuration: `$ gcloud auth configure-docker`
1. Create a Cloud-SQL instance, database and user.
1. Create a service account with the role Cloud-SQL Client and download a private key.
1. Activate service account `$ gcloud auth activate-service-account --key-file /path/to/key-file.json`

## Initial setup

### Build and push container image

    $ docker build -t gcr.io/fixmyberlin-201008/fixmyberlin:0.1 .
    $ docker push gcr.io/fixmyberlin-201008/fixmyberlin:0.1

### Create cluster

    $ gcloud container clusters create fixmyberlin --num-nodes 4 --image-type g1-small --disk-size 10

### Create database secrets: 

    $ kubectl create secret generic cloudsql-oauth-credentials --from-file /path/to/key-file.json
    $ kubectl create secret generic cloudsql --from-literal username=[DATABASE_USER] --from-literal password=[DATABASE_PASSWORD]

### Create deployment

    $ kubectl create -f deployment.yml

### Create bucket for static resources

    $ gsutil mb gs://fixmyberlin-201008
    $ gsutil defacl set public-read gs://fixmyberlin-201008

### Collect and upload static resources

    $ docker-compose run app python manage.py collectstatic
    $ gsutil rsync -R static/ gs://fixmyberlin-201008/static

## Upgrade deployment

1. Build and push a new container image with a new version tag. 
1. Change the image version for the fixmyberlin-app container in the deployment configuration via `kubectl edit deployment/fixmyberlin` or the Google Cloud Platform Console.
1. Collect new static resources and upload them to the bucket.
