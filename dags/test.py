from datetime import datetime
import os

from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023,6,20),
    'retries': 0
}


with DAG('2_Test_Badge_5', default_args=default_args, schedule_interval='@once') as dag:

    task_test_stage = BashOperator(
        task_id='test_create_stage',
        bash_command='cd /dbt && dbt run-operation create_stage --args \'{"stage_name": "uni_kishore_pipeline", "stage_url": "s3://uni-kishore-pipeline", "dry_run": false}\'',
        env={
            'dbt_user': '{{ var.value.dbt_user }}',
            'dbt_password': '{{ var.value.dbt_password }}',
            **os.environ
        },
        dag=dag
    )

task_test_stage