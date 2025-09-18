#!/usr/bin/env bash

cd "$(dirname "$0")"

LOCAL_TAG=`date +"%Y-%m-%d-%H-%M"`
export LOCAL_IMAGE_NAME="stream-model-duration:${LOCAL_TAG}"
export PREDICTIONS_STREAM_NAME="ride_predictions"

echo ${LOCAL_IMAGE_NAME}, ${PREDICTIONS_STREAM_NAME}

docker build -t ${LOCAL_IMAGE_NAME} ..

docker-compose up -d

sleep 15
pipenv run python test_docker.py

ERROR_CODE=$?
if [ ${ERROR_CODE} -ne 0 ]; then
    docker-compose logs
    docker-compose stop
    exit ${ERROR_CODE}
fi

sleep 5
pipenv run python test_kinesis.py

ERROR_CODE=$?
if [ ${ERROR_CODE} -ne 0 ]; then
    docker-compose logs
    docker-compose stop
    exit ${ERROR_CODE}
fi

docker-compose stop
