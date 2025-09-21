#!/usr/bin/env bash

cd "$(dirname "$0")"
export LOCAL_IMAGE_NAME=$1
if [ "${LOCAL_IMAGE_NAME}" == "" ]; then
    echo "The local image isn't set hence we are buildng the image" 
    LOCAL_TAG=`date +"%Y-%m-%d-%H-%M"`
    export LOCAL_IMAGE_NAME="stream-model-duration:${LOCAL_TAG}"
    docker build -t ${LOCAL_IMAGE_NAME} ..
else
    echo "No need to build the docker image ${LOCAL_IMAGE_NAME}"
fi

 export PREDICTIONS_STREAM_NAME="ride_predictions"

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
