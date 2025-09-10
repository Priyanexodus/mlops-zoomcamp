import json
import os
import base64
import boto3
import mlflow

def get_model_location(model_id):
    model_location = os.getenv('MODEL_LOCATION')

    if model_location is not None:
        return model_location

    model_bucket = os.getenv('MODEL_BUCKET', 'priyan-mlflow-artifacts')
    experiment_id = os.getenv('MLFLOW_EXPERIMENT_ID', '1')

    model_location = f's3://{model_bucket}/{experiment_id}/models/{model_id}/artifacts/'
    return model_location

def load_model(model_id):
    model_path = get_model_location(model_id)
    model = mlflow.pyfunc.load_model(model_path)
    return model

def base64_decode(encoded_data):
    decoded_data = base64.b64decode(encoded_data).decode('utf-8')
    ride_event = json.loads(decoded_data)
    return ride_event

class ModelService():
    def __init__(self, model, model_version=None, callbacks=None):
        self.model_version = model_version
        self.model = model
        self.callbacks = callbacks or []
        
    def prepare_features(self,ride):
        features = {}
        features["PU_DO"] = f'{ride["PULocationID"]}_{ride["DOLocationID"]}'
        features["trip_distance"] = ride["trip_distance"]
        return features


    def predict(self,features):
        preds = self.model.predict(features)
        return float(preds[0])


    def lambda_handler(self,event,context=None):
        # pylint: disable=unused-argument
        # print(json.dumps(event))

        predictions = []

        for record in event["Records"]:
            encoded_data = record["kinesis"]["data"]
            decoded_data = base64_decode(encoded_data)
            ride_event = json.loads(json.dumps(decoded_data))

            # print((ride_event))

            ride = ride_event["ride"]
            ride_id = ride_event["ride_id"]
            features = self.prepare_features(ride)
            prediction = self.predict(features)

        prediction_event = {
            "model": "ride_duration_prediction_model",
            "version": self.model_version,
            "prediction": {"ride_duration": prediction, "ride_id": ride_id},
        }        

        for callback in self.callbacks:
            callback(prediction_event)           
        
        predictions.append(prediction_event)
        return {"predictions": predictions}
    
class KinesisCallback:
    def __init__(self, kinesis_client, prediction_stream_name):
        self.kinesis_client = kinesis_client
        self.prediction_stream_name = prediction_stream_name

    def put_record(self, prediction_event):
        ride_id = prediction_event['prediction']['ride_id']

        self.kinesis_client.put_record(
            StreamName=self.prediction_stream_name,
            Data=json.dumps(prediction_event),
            PartitionKey=str(ride_id),
        )
        
def create_kinesis_client():
    endpoint_url = os.getenv("KINESIS_ENDPOINT_URL")
    
    if endpoint_url is not None:
        return boto3.client("kinesis", endpoint_url=endpoint_url)
    return boto3.client("kinesis")

def init(model_id:str, run_id:str, test_run:bool, predictions_stream_name:str):
    
    model = load_model(model_id)
    callbacks = []
    if not test_run: 
        kinesis_client = create_kinesis_client()
        kinesis_callback = KinesisCallback(kinesis_client, predictions_stream_name)
        callbacks.append(kinesis_callback.put_record)
        
    model_service = ModelService(model=model,
                                 model_version=run_id,
                                 callbacks=callbacks)
    return model_service
