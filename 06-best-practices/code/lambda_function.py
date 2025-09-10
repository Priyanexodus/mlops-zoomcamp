import os
import model

RUN_ID = os.getenv("RUN_ID")
MODEL_ID = os.getenv("MODEL_ID")
PREDICTIONS_STREAM_NAME = os.getenv("PREDICTIONS_STREAM_NAME")
TEST_RUN = os.getenv("TEST_RUN", default="False") == "True"


model_service = model.init(model_id=MODEL_ID,
                            predictions_stream_name=PREDICTIONS_STREAM_NAME,
                            test_run=TEST_RUN,
                            run_id=RUN_ID)

def lambda_handler(event,context):
    # pylint: disable=unused-argument
    return model_service.lambda_handler(event)
