from airflow.sdk import Asset, dag, task
from datetime import datetime
import pandas as pd
import os
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LinearRegression
import pickle
import mlflow

@dag(start_date=datetime(2025, 6, 5), schedule=None, tags=['Price Prediction'])
def prediction_pipeline():

    @task()
    def read_file():
        df = pd.read_parquet(r"https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-03.parquet")
        print(f"Records loaded: {len(df)}")
        
    @task
    def preprocessed(filename):
        df = pd.read_parquet(filename)
        print(f"Records loaded: {len(df)}")
        df['duration'] = df.tpep_dropoff_datetime - df.tpep_pickup_datetime
        df.duration = df.duration.dt.total_seconds() / 60

        df = df[(df.duration >= 1) & (df.duration <= 60)]

        categorical = ['PULocationID', 'DOLocationID']
        df[categorical] = df[categorical].astype(str)
        
        file_dir = "/tmp/data"
        os.makedirs(file_dir, exist_ok=True)

        file_path = os.path.join(file_dir, "my_data.parquet")
        df.to_parquet(file_path, index=False)
        return file_path
  
    
    @task
    def train_model(**context):
        
        ti = context['ti']
        file_path = ti.xcom_pull(task_ids='preprocessed')
        df = pd.read_parquet(file_path)
        
        df['PU_DO'] = df['PULocationID'] + "_" + df['DOLocationID']
        dv = DictVectorizer()
        train_dicts = df[['PULocationID', 'DOLocationID']].to_dict(orient='records')
        X_train = dv.fit_transform(train_dicts)
        y_train = df['duration']

        model = LinearRegression()
        model.fit(X_train, y_train)

        print(f"Intercept: {round(model.intercept_, 2)}")
        
        file_dir = "/tmp/models"
        os.makedirs(file_dir, exist_ok=True)
        
        file_path = os.path.join(file_dir, "model.bin")
        
        with open(file_path, 'wb') as f_out:
            pickle.dump((dv, model), f_out)
            
        return file_path

    @task
    def register_model(**context):
        
        ti = context['ti']
        file_path = ti.xcom_pull(task_ids='train_model')
        
        with open(file_path, 'rb') as f_in:
            dv, model = pickle.load(f_in)

        mlflow.set_tracking_uri("sqlite:///mlflow.db")
        mlflow.set_experiment("nyc-taxi-experiment")

        with mlflow.start_run():
            mlflow.sklearn.log_model(model, "model")
            mlflow.log_artifact(file_path)

            mlflow.log_param("model_type", "LinearRegression")
            mlflow.log_metric("intercept", model.intercept_)

            info = mlflow.active_run().info
            print(f"Model logged in: {info.artifact_uri}")

    file_path = preprocessed("https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-03.parquet")
    train = train_model()
    log = register_model()
    
    file_path >> train>>log
prediction_pipeline()