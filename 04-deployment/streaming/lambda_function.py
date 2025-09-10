import json
import base64
import boto3
import os
import mlflow

RUN_ID = os.getenv("RUN_ID")
MODEL_ID = os.getenv("MODEL_ID")
STREAM_NAME = os.getenv("STREAM_NAME")
TEST_RUN = os.getenv("TEST_RUN", default="False") == "True"

kinesis_client = boto3.client("kinesis")

logged_model = f"s3://priyan-mlflow-artifacts/1/models/{MODEL_ID}/artifacts/"
model = mlflow.pyfunc.load_model(logged_model)


def prepare_features(ride):
    features = {}
    features["PU_DO"] = "%s_%s" % (ride["PULocationID"], ride["DOLocationID"])
    features["trip_distance"] = ride["trip_distance"]
    return features


def predict(features):
    preds = model.predict(features)
    return float(preds[0])


def lambda_handler(event, context=None):
    # print(json.dumps(event))

    predictions = []

    for record in event["Records"]:
        encoded_data = record["kinesis"]["data"]
        decoded_data = base64.b64decode(encoded_data).decode("utf-8")
        ride_event = json.loads(json.loads(json.dumps(decoded_data)))

        # print((ride_event))

        ride = ride_event["ride"]
        ride_id = ride_event["ride_id"]
        features = prepare_features(ride)
        prediction = predict(features)

    prediction_event = {
        "model": "ride_duration_prediction_model",
        "version": "123",
        "prediction": {"ride_duration": prediction, "ride_id": ride_id},
    }
    if not TEST_RUN:
        kinesis_client.put_record(
            StreamName=STREAM_NAME,
            Data=json.dumps(prediction_event),
            PartitionKey=str(ride_id),
        )
    predictions.append(prediction_event)

    return {"predictions": predictions}
