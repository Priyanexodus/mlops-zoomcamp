import datetime
import time
import random
import logging
import uuid
import pytz
import pandas as pd
import io
import joblib
import psycopg

from evidently import DataDefinition, Regression, Dataset, Report
from evidently.presets import DataDriftPreset
from evidently.metrics import DriftedColumnsCount, DuplicatedColumnsCount

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s"
)

SEND_TIMEOUT = 10
rand = random.Random()

create_table_statement = """
drop table if exists dummy_metrics;
create table dummy_metrics(
	timestamp timestamp,
	prediction_drift float,
	num_drifted_cols integer,
	num_dup_cols integer
)
"""
# The ideal data in which the model had been trained with
reference_data = pd.read_parquet(r"./data/reference.parquet")

# unpacking the trained model
with open(r"./model/liner_reg.bin", "rb") as fp:
    model = joblib.load(fp)

# getting the whole data to simulate the production
raw_data = pd.read_parquet(r"./data/green_tripdata_2022-02.parquet")

# specifing the initial start date for the data
begin = datetime.datetime(2022, 2, 1, 0, 0)

# data labelling
target = "duration_min"
nums = ["passenger_count", "trip_distance", "fare_amount", "total_amount"]
cat = ["PULocationID", "DOLocationID"]

# Defining the schema for the dataframe for evidently report
schema = DataDefinition(
    numerical_columns=nums + ["prediction"],
    categorical_columns=cat,
    regression=[Regression(target=target, prediction="prediction")],
)

# Creating the structure of the report

report = Report([DataDriftPreset(), DriftedColumnsCount(), DuplicatedColumnsCount()])


def prep_db():
    with psycopg.connect(
        "host=localhost port=5432 user=postgres password=example", autocommit=True
    ) as conn:
        res = conn.execute("SELECT 1 FROM pg_database WHERE datname='test'")
        if len(res.fetchall()) == 0:
            conn.execute("create database test;")
        with psycopg.connect(
            "host=localhost port=5432 dbname=test user=postgres password=example"
        ) as conn:
            conn.execute(create_table_statement)


def calculate_metrics_postgresql(curr, i):
    # filtering the data with the specified date
    current_data = raw_data[
        (raw_data["lpep_pickup_datetime"] >= (begin + datetime.timedelta(i)))
        & (raw_data["lpep_pickup_datetime"] < (begin + datetime.timedelta(i + 1)))
    ]
    # handling null values
    current_data.fillna(0, inplace=True)

    # making the model predict and store it's value in the current_data
    current_data["prediction"] = model.predict(current_data[cat + nums])

    # creating the evidently dataset
    reference_set = Dataset.from_pandas(reference_data, data_definition=schema)

    current_set = Dataset.from_pandas(current_data, data_definition=schema)

    # creating report
    my_eval = report.run(reference_set, current_set)
    result = my_eval.dict()

    # input dictionary (short name for convenience)
    metrics = result["metrics"]

    # desired keys and partial matching strings
    key_map = {
        "prediction_drift": "ValueDrift(column=prediction)",
        "num_drifted_cols": "DriftedColumnsCount",
        "num_dup_cols": "DuplicatedColumnsCount",
    }

    # result dictionary
    result = {}

    for key, match_str in key_map.items():
        for metric in metrics:
            if match_str in metric["metric_id"]:
                val = metric["value"]
                # if it's a dict (e.g., DriftedColumnsCount), get count
                result[key] = val["count"] if isinstance(val, dict) else float(val)
                break

    prediction_drift = result.get("prediction_drift")
    num_drifted_cols = int(result.get("num_drifted_cols"))
    num_dup_cols = int(result.get("num_dup_cols"))

    curr.execute(
        "insert into dummy_metrics(timestamp, prediction_drift, num_drifted_cols, num_dup_cols) values (%s, %s, %s, %s)",
        (
            begin + datetime.timedelta(i),
            prediction_drift,
            num_drifted_cols,
            num_dup_cols,
        ),
    )


def main():
    prep_db()
    last_send = datetime.datetime.now() - datetime.timedelta(seconds=10)
    with psycopg.connect(
        "host=localhost port=5432 dbname=test user=postgres password=example",
        autocommit=True,
    ) as conn:
        for i in range(0, 100):
            with conn.cursor() as curr:
                calculate_metrics_postgresql(curr, i)

            new_send = datetime.datetime.now()
            seconds_elapsed = (new_send - last_send).total_seconds()
            if seconds_elapsed < SEND_TIMEOUT:
                time.sleep(SEND_TIMEOUT - seconds_elapsed)
            while last_send < new_send:
                last_send = last_send + datetime.timedelta(seconds=10)
            logging.info("data sent")


if __name__ == "__main__":
    main()
