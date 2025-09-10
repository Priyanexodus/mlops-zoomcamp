import os
import pickle
import click

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import root_mean_squared_error

import mlflow

mlflow.set_tracking_uri("sqlite:///random_forest.db")
mlflow.set_experiment("RandomForest")

def load_pickle(filename: str):
    with open(filename, "rb") as f_in:
        return pickle.load(f_in)


@click.command()
@click.option(
    "--data_path",
    default="./output",
    help="Location where the processed NYC taxi trip data was saved"
)
def run_train(data_path: str):
    with mlflow.start_run():
    
        mlflow.set_tag("developer", "Priyadharshan")
        
        train_path = os.path.join(data_path, "train.pkl")
        mlflow.log_param("train_data_path", train_path)
        
        test_path = os.path.join(data_path, "val.pkl")
        mlflow.log_param("test_data_path", test_path)

        X_train, y_train = load_pickle(train_path)
        X_val, y_val = load_pickle(test_path)

        rf = RandomForestRegressor(max_depth=10, random_state=0)
        rf.fit(X_train, y_train)
        y_pred = rf.predict(X_val)

        rmse = (mean_squared_error(y_val, y_pred))**0.5
        mlflow.log_metric("rsme", rsme)
        mlflow.sklearn.log_model(rf, artifact_path="models_mlflows")


if __name__ == '__main__':
    run_train()