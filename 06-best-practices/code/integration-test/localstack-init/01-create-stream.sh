#!/usr/bin/env bash
set -e

echo "Creating Kinesis stream: ride_predictions"

awslocal kinesis create-stream \
  --stream-name ride_predictions \
  --shard-count 1

awslocal kinesis wait stream-exists \
  --stream-name ride_predictions

echo `awslocal kinesis list-streams`