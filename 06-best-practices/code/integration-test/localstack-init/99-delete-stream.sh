#!/usr/bin/env bash
set -e

echo "Deleting Kinesis stream: ride_predictions"

awslocal kinesis delete-stream \
  --stream-name ride_predictions \
  --enforce-deletion || true
