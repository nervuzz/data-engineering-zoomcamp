import os
from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
BUCKET = os.environ.get("GCP_GCS_BUCKET")
BIGQUERY_DATASET = os.environ.get("BIGQUERY_DATASET", 'trips_data_all')
GCP_SERVICE_ACCOUNT_KEY = "/.google/credentials/google_credentials.json"

dataset_url = "https://s3.amazonaws.com/nyc-tlc/trip+data/"
path_to_local_home = os.environ.get("AIRFLOW_HOME", "/opt/airflow/")


def csv_to_parquet(file_path: str) -> None:
    import logging

    import pyarrow.csv as pv
    import pyarrow.parquet as pq

    if not file_path.endswith(".csv"):
        logging.error("Can only accept files in CSV format")
        return
    table = pv.read_csv(file_path)
    pq.write_table(table, file_path.replace(".csv", ".parquet"))


default_args = {
    "owner": "airflow",
    "start_date": datetime(2019, 1, 1),
    "end_date": datetime(2019, 12, 1),
    "depends_on_past": False,
    "retries": 1,
    "max_active_tasks": 2,
}

with DAG(
    dag_id="for_hire_veh_to_gcs_dag",
    schedule_interval="@monthly",
    default_args=default_args,
    catchup=True,
    max_active_runs=2,
    tags=["dtc-de"],
) as dag:

    dataset = "fhv_tripdata_{{ macros.ds_format(ds, '%Y-%m-%d', '%Y-%m') }}"

    download_dataset = BashOperator(
        task_id="download_dataset",
        bash_command=f"curl -fsS {dataset_url+dataset}.csv > {path_to_local_home}/raw/{dataset}.csv"
    )

    convert_csv_to_parquet = PythonOperator(
        task_id="convert_to_parquet",
        python_callable=csv_to_parquet,
        op_kwargs={
            "file_path": f"{path_to_local_home}/raw/{dataset}.csv",
        },
    )

    upload_to_gcs = BashOperator(
        task_id="upload_to_gcs",
        bash_command=f"gcloud auth activate-service-account --key-file={GCP_SERVICE_ACCOUNT_KEY} && \
        gsutil -m cp {path_to_local_home}/raw/{dataset}.parquet gs://{BUCKET}",
    )

    download_dataset >> convert_csv_to_parquet >> upload_to_gcs
