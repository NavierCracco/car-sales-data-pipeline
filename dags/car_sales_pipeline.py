from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator

default_args = {
    'owner': 'Navier Cracco',
    'depends_on_past': False,
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(seconds=15)
}

with DAG(
    'car_sales_data_pipeline',
    default_args=default_args,
    description='A DAG to process and load car sales data into Snowflake',
    schedule_interval='@monthly',
    start_date=datetime(2018, 3, 1),
    catchup=True,
    tags=['ingest', 'snowflake', 'production']
) as dag:
    
    start = EmptyOperator(task_id='start')

    ingest_to_snowflake = BashOperator(
        task_id='ingest_to_snowflake',
        bash_command='python /opt/airflow/code/extract_load/src/ingest_to_snowflake.py {{ ds }}'
    )

    end = EmptyOperator(task_id='end')

    start >> ingest_to_snowflake >> end