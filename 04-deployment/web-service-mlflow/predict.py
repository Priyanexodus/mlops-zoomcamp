import os
import pickle

import mlflow
from flask import Flask, request, jsonify


RUN_ID = "fef1f2c02c0348dba3dec6a98bbc958a"
mlflow.set_tracking_uri("http://127.0.0.1:5000")
model_uri = "runs:/c6bf9901fea34381a0c8b6d8297fec81/model"
model = mlflow.pyfunc.load_model(model_uri)


def prepare_features(ride):
    features = {}
    features['PU_DO'] = '%s_%s' % (ride['PULocationID'], ride['DOLocationID'])
    features['trip_distance'] = ride['trip_distance']
    return features


def predict(features):
    preds = model.predict(features)
    return float(preds[0])


app = Flask('duration-prediction')


@app.route('/predict', methods=['POST'])
def predict_endpoint():
    ride = request.get_json()

    features = prepare_features(ride)
    pred = predict(features)

    result = {
        'duration': pred,
        'model_version': RUN_ID
    }

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=9696)
