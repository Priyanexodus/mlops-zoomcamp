def expected_prediction() -> dict:
    return {
        "predictions": [
            {
                "model": "ride_duration_prediction_model",
                "version": "test123",
                "prediction": {
                    "ride_duration": 12.265893054405405,
                    "ride_id": 156,
                },
            }
        ]
    }