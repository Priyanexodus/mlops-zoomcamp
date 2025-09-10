from pathlib import Path
import model

def read_data(file):
    test_directory = Path(__file__).parent
    with open(test_directory/file, "rt", encoding="utf-8") as fp:
        data = fp.read().strip()
        return data
    
def test_base64_decode():
    base64_input = read_data("data.b64")

    actual_result = model.base64_decode(base64_input)
    expected_result = {
        "ride": {
            "PULocationID": 130,
            "DOLocationID": 205,
            "trip_distance": 3.66,
        },
        "ride_id": 156,
    }

    assert actual_result == expected_result
    
def test_prepare_features():
    """
    This function validates whether the preprocessing is upto the standard
    """
    model_service = model.ModelService(None)

    ride = {
        "PULocationID": 130,
        "DOLocationID": 205,
        "trip_distance": 3.66,
    }

    actual_features = model_service.prepare_features(ride)

    expected_features = {
        "PU_DO": "130_205",
        "trip_distance": 3.66,
    }

    assert actual_features == expected_features

class MockModel:   
    def __init__(self, value):
        self.value = value      
    def predict(self, X):
        # pylint: disable=invalid-name
        n = len(X)
        return [self.value]*n

def test_predict():
    mock_model = MockModel(10)    
    model_service = model.ModelService(mock_model)
    features = {
        "PU_DO": "130_205",
        "trip_distance": 3.66,
    }

    actual_prediction = model_service.predict(features)
    expected_prediction = 10.0
    
    assert actual_prediction == expected_prediction    

def test_lambda_handler():
    mock_model = MockModel(10) 
    model_version = "Test123"   
    model_service = model.ModelService(mock_model, model_version)
    base64_input = read_data("data.b64")
    
    event = {
    "Records": [
        {
            "kinesis": {
                "data": base64_input,
                },
           }]
}

    actual_prediction = model_service.lambda_handler(event)
    expected_prediction = {"predictions": [
        {
            "model": "ride_duration_prediction_model",
            "version": model_version,
            "prediction": {"ride_duration": 10.0, "ride_id": 156},
        }
    ]}
    
    assert actual_prediction == expected_prediction
    