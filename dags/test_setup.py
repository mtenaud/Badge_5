import os
from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from airflow.operators.dagrun_operator import TriggerDagRunOperator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023,6,27),
    'retries': 0
}

dag_setup = DAG('2_Test_Badge_5_Setup', 
                default_args=default_args, 
                start_date=default_args['start_date'],
                schedule_interval='@once')

def airflow_task_decorator(task_id, bash_command):
    def decorator(func):
        def wrapper(dag):
            return BashOperator(
                task_id=task_id,
                bash_command=bash_command,
                env={
                    'dbt_user': '{{ var.value.dbt_user }}',
                    'dbt_password': '{{ var.value.dbt_password }}',
                    **os.environ
                },
                dag=dag
            )
        return wrapper
    return decorator

@airflow_task_decorator('load_seed_todl_once', 
                        'cd /dbt && dbt seed --profiles-dir .')
def task_seed(dag):
    pass

@airflow_task_decorator('create_stage', 
                        'cd /dbt && dbt run-operation create_stage --args \'{\
                            "stage_name": "uni_kishore_pipeline", \
                            "stage_url": "s3://uni-kishore-pipeline", \
                            "dry_run": false}\'')
def task_stage(dag):
    pass

@airflow_task_decorator('create_file_format',
                        'cd /dbt && dbt run-operation create_file_format --args \'{\
                            "file_format_name": "ff_json_logs", \
                            "file_format_type": "JSON", \
                            "strip_outer_array": true, \
                            "dry_run": false}\'')
def task_file_format(dag):
    pass

@airflow_task_decorator('create_ed_pipeline_logs',
                        'cd /dbt && dbt run --model ed_pipeline_logs')
def task_ed_pipeline_logs(dag):
    pass

@airflow_task_decorator('create_pipe', 
                        'cd /dbt && dbt run-operation create_pipe --args \'{\
                            "pipe_name": "get_new_files", \
                            "table_name": "ed_pipeline_logs", \
                            "dry_run": false}\'')
def task_pipe(dag):
    pass

@airflow_task_decorator('create_stream', 
                        'cd /dbt && dbt run-operation create_stream --args \'{\
                            "stream_name": "ed_cdc_stream", \
                            "table_name": "ed_pipeline_logs", \
                            "dry_run": false}\'')
def task_stream(dag):
    pass

@airflow_task_decorator('create_logs_enhanced',
                        'cd /dbt && dbt run --model logs_enhanced')
def task_logs_enhanced(dag):
    pass

begin = EmptyOperator(task_id="debut")
to_seed = task_seed(dag_setup)
create_stage = task_stage(dag_setup)
create_file_format = task_file_format(dag_setup)
create_ed_pipeline_logs = task_ed_pipeline_logs(dag_setup)
create_pipe = task_pipe(dag_setup)
create_stream = task_stream(dag_setup)
create_logs_enhanced = task_logs_enhanced(dag_setup)
dag_unpauser = BashOperator(
                        task_id='unpause_dag',
                        bash_command='airflow dags unpause 2_Test_Badge_5_Loop',
                        dag = dag_setup)

trigger_dag = TriggerDagRunOperator(
                        task_id='trigger_dag',
                        trigger_dag_id='2_Test_Badge_5_Loop',
                        dag=dag_setup,
                        execution_date="{{ execution_date + macros.timedelta(minutes=5) }}")

begin >> [create_stage, create_file_format, to_seed]
[create_stage, create_file_format] >> create_ed_pipeline_logs >> create_pipe >> create_stream 
[create_stream , to_seed] >> create_logs_enhanced
create_logs_enhanced >> dag_unpauser >> trigger_dag