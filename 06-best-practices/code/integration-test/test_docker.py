import json

import requests
import test_utils
from deepdiff import DeepDiff

with open("event.json", "rt", encoding="utf-8") as f_in:
    event = json.load(f_in)

URL = "http://localhost:8080/2015-03-31/functions/function/invocations"

actual_response = requests.post(url=URL, json=event, timeout=5).json()
print(json.dumps(actual_response, indent=2))
expected_response = test_utils.expected_prediction()

difference = DeepDiff(actual_response, expected_response, significant_digits=1)
print(difference)

assert "type_changes" not in difference
assert "value_changed" not in difference
