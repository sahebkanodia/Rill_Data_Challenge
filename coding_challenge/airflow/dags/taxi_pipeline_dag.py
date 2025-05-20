from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.models import Variable
from airflow.utils.dates import days_ago
import sys
import os
from typing import Tuple

# Set up the base directory. refer to docker-compose.yml for the path
base_dir = "/opt/airflow"

from scripts.download_data import DataDownloader

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,  # Changed to False to allow tasks to run without previous successful runs
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),    # TODO: We can also enable exponential backoff here
}

def get_next_month_year(current_year: int, current_month: int) -> Tuple[int, int]:
    """Calculate the next month and year to process."""
    if current_month == 12:
        return current_year + 1, 1
    return current_year, current_month + 1

def get_or_initialize_processing_state() -> Tuple[int, int]:
    """Get the last processed month/year or initialize if not exists."""
    try:
        last_year = int(Variable.get("last_processed_year"))
        last_month = int(Variable.get("last_processed_month"))
    except:
        # If no checkpoint exists, start from January 2013 because schema is different for earlier years
        last_year = 2013
        last_month = 1
        Variable.set("last_processed_year", last_year)
        Variable.set("last_processed_month", last_month)
    return last_year, last_month

def update_processing_state(year, month):
    """Update the last processed month/year in Airflow variables."""
    Variable.set("last_processed_year", year)
    Variable.set("last_processed_month", month)


def download_data_task(**context):
    """Task to download taxi and zone data."""
    # Get the last processed month/year
    year, month = get_or_initialize_processing_state()
    
    # Validate we're not trying to process future data
    current_date = datetime.now()
    target_date = datetime(year, month, 1)
    if target_date > current_date:
        raise ValueError(f"Cannot process future data: {year}-{month}")
    
    data_dir = f"{base_dir}/data"
    downloader = DataDownloader(data_dir)
    
    # Download zone data (if not exists)
    zone_file = downloader.download_zone_data()
    
    # Download taxi data for the target month
    taxi_file = downloader.download_taxi_data(year, month)
    
    # Calculate next month/year for the next run
    next_year, next_month = get_next_month_year(year, month)
    
    # Update the state for next run
    update_processing_state(next_year, next_month)
    
    # Push the file paths to XCom for downstream tasks
    context['task_instance'].xcom_push(key='zone_file', value=zone_file)
    context['task_instance'].xcom_push(key='taxi_file', value=taxi_file)
    context['task_instance'].xcom_push(key='year', value=year)
    context['task_instance'].xcom_push(key='month', value=month)



# Create the DAG
with DAG(
    'nyc_taxi_pipeline_ingestion',
    default_args=default_args,
    description='NYC Taxi Data Pipeline',
    schedule_interval='0 */1 * * *',  # Run every hour
    start_date=days_ago(1),
    max_active_runs=1,
    catchup=False,
    tags=['taxi', 'etl'],
) as dag:
    
    # Task to download data
    download_task = PythonOperator(
        task_id='download_data',
        python_callable=download_data_task
    )
    
    # Task to run Spark job
    spark_task = BashOperator(
        task_id='run_spark_job',
        bash_command="""
        docker exec \
            -e PYTHONPATH=/opt/bitnami/spark/scripts \
            coding_challenge-spark-1 \
            spark-submit \
                --master spark://spark:7077 \
                --deploy-mode client \
                --driver-memory 2g \
                --executor-memory 4g \
                --executor-cores 2 \
                --packages org.apache.spark:spark-sql_2.12:3.4.1,com.clickhouse:clickhouse-jdbc:0.4.6,org.apache.commons:commons-lang3:3.12.0 \
                --conf spark.driver.host=spark \
                --conf spark.driver.bindAddress=0.0.0.0 \
                --conf spark.network.timeout=600s \
                --conf spark.executor.heartbeatInterval=60s \
                /opt/bitnami/spark/scripts/jobs/taxi_etl.py \
                --taxi-data {{ task_instance.xcom_pull(task_ids='download_data', key='taxi_file') }} \
                --zone-data {{ task_instance.xcom_pull(task_ids='download_data', key='zone_file') }} \
                --output {{ params.base_dir }}/data/processed \
                --year {{ task_instance.xcom_pull(task_ids='download_data', key='year') }} \
                --month {{ task_instance.xcom_pull(task_ids='download_data', key='month') }}
        """,
        params={'base_dir': base_dir},
        dag=dag
    )
    
    # Define task dependencies
    download_task >> spark_task