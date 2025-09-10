import os
import pickle
import mlflow
from flask import Flask, request, jsonify


RUN_ID = os.getenv("RUN_ID")
MODEL_ID = os.getenv("MODEL_ID")

"""
TRACKING_SERVER_HOST = "ec2-13-60-50-147.eu-north-1.compute.amazonaws.com"  # fill in wih the public DNS of the EC2 instance
mlflow.set_tracking_uri(f"http://{TRACKING_SERVER_HOST}:5000")
logged_model = f"runs:/{RUN_ID}/model"
"""

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


app = Flask("duration-prediction")


@app.route("/predict", methods=["POST"])
def predict_endpoint():
    ride = request.get_json()

    features = prepare_features(ride)
    pred = predict(features)

    result = {"duration": pred, "model_version": RUN_ID}

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=9696)
