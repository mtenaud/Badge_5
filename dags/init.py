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


with DAG('1_init_once_seed_todl', default_args=default_args, schedule_interval='@once') as dag:
    task_seed = BashOperator(
        task_id='load_seed_todl_once',
        bash_command='cd /dbt && dbt seed --profiles-dir .',
        env={
            'dbt_user': '{{ var.value.dbt_user }}',
            'dbt_password': '{{ var.value.dbt_password }}',
            **os.environ
        },
        dag=dag
    )

task_seed