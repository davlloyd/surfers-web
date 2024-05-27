#! /bin/bash

# Script to generate and publish techdopcs from current directory to gcs
#export GOOGLE_APPLICATION_CREDENTIALS=~/gcr.json
export AWS_ACCESS_KEY_ID=HGzn7adbfnf87TE1Vj57
export AWS_SECRET_ACCESS_KEY=B9eoCa2w0Zi0TlmwmPV2ipJGF8QZol0JTXKAcqwo
export AWS_REGION=au-syd-1

techdocs-cli generate --source-dir . 
techdocs-cli publish --publisher-type awsS3 --storage-name techdocs  --awsEndpoint http://minio.home.local:9000 --awsS3ForcePathStyle --entity alpha/Component/surfersweb

